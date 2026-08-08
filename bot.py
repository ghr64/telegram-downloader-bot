#!/usr/bin/env python3
"""
Telegram YouTube/Instagram Downloader Bot
Downloads videos from YouTube and Instagram using yt-dlp
Automatically splits files that exceed Telegram's limits
"""

import os
import logging
import asyncio
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import yt_dlp

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DOWNLOAD_DIR = Path('./downloads')
TELEGRAM_FILE_LIMIT = 2000 * 1024 * 1024  # 2GB limit for bots
CHUNK_SIZE = 1900 * 1024 * 1024  # 1.9GB per chunk to be safe

# Ensure download directory exists
DOWNLOAD_DIR.mkdir(exist_ok=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = (
        "👋 Welcome to the Video Downloader Bot!\n\n"
        "📥 Send me a YouTube or Instagram URL and I'll download it for you.\n\n"
        "✨ Features:\n"
        "• Download videos from YouTube and Instagram\n"
        "• Automatic file splitting if video exceeds Telegram limits\n"
        "• High quality downloads\n\n"
        "Commands:\n"
        "/start - Show this message\n"
        "/help - Get help\n\n"
        "Just send a URL to get started! 🚀"
    )
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "🆘 How to use this bot:\n\n"
        "1. Copy a YouTube or Instagram video URL\n"
        "2. Send it to me\n"
        "3. Wait for the download and processing\n"
        "4. Receive your video!\n\n"
        "If the video is larger than 2GB, I'll split it into parts automatically.\n\n"
        "Supported platforms:\n"
        "• YouTube (youtube.com, youtu.be)\n"
        "• Instagram (instagram.com)\n"
        "• And many more supported by yt-dlp!"
    )
    await update.message.reply_text(help_text)


def split_file(file_path: Path, chunk_size: int = CHUNK_SIZE) -> List[Path]:
    """Split a file into chunks."""
    file_size = file_path.stat().st_size
    
    if file_size <= TELEGRAM_FILE_LIMIT:
        return [file_path]
    
    logger.info(f"File size {file_size} bytes exceeds limit. Splitting...")
    
    chunks = []
    chunk_num = 1
    
    with open(file_path, 'rb') as f:
        while True:
            chunk_data = f.read(chunk_size)
            if not chunk_data:
                break
            
            chunk_path = file_path.parent / f"{file_path.stem}_part{chunk_num}{file_path.suffix}"
            with open(chunk_path, 'wb') as chunk_file:
                chunk_file.write(chunk_data)
            
            chunks.append(chunk_path)
            chunk_num += 1
            logger.info(f"Created chunk {chunk_num - 1}: {chunk_path.name}")
    
    return chunks


def download_video(url: str, user_id: int) -> Optional[Path]:
    """Download video using yt-dlp with multiple strategies."""
    user_download_dir = DOWNLOAD_DIR / str(user_id)
    user_download_dir.mkdir(exist_ok=True)
    
    output_template = str(user_download_dir / '%(title)s.%(ext)s')
    
    # Check for cookies file
    cookies_file = Path('./cookies.txt')
    
    # Strategies that don't require Deno (most reliable)
    strategies = [
        {'name': 'web_embedded', 'client': 'web_embedded'},
        {'name': 'mweb', 'client': 'mweb'},
        {'name': 'android_vr', 'client': 'android_vr'},
        {'name': 'tv_embedded', 'client': 'tv_embedded'},
        {'name': 'web_default', 'client': 'web,default'},
        {'name': 'android', 'client': 'android'},
    ]
    
    for strategy in strategies:
        strategy_name = strategy['name']
        logger.info(f"Trying strategy: {strategy_name}")
        
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': output_template,
            'merge_output_format': 'mp4',
            'quiet': False,
            'cookiefile': str(cookies_file) if cookies_file.exists() else None,
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
                'Accept-Language': 'en-US,en;q=0.9',
            },
            'retries': 5,
            'extractor_args': {'youtube': {'player_client': [strategy['client']]}}
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                video_path = Path(filename)
                
                if video_path.exists() and video_path.stat().st_size > 0:
                    logger.info(f"✅ Download successful: {strategy_name}")
                    return video_path
                    
        except Exception as e:
            logger.warning(f"Strategy {strategy_name} failed: {e}")
            continue
    
    raise Exception("All download strategies failed")


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle URLs sent by users."""
    url = update.message.text.strip()
    user_id = update.effective_user.id
    
    if not (url.startswith('http://') or url.startswith('https://')):
        await update.message.reply_text("❌ Please send a valid URL starting with http:// or https://")
        return
    
    status_message = await update.message.reply_text("⏳ Processing your request...")
    
    try:
        await status_message.edit_text("📥 Downloading video... (may take a while)")
        
        video_path = download_video(url, user_id)
        
        if not video_path or not video_path.exists():
            await status_message.edit_text("❌ Download failed. Please try again.")
            return
        
        file_size = video_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        
        await status_message.edit_text(f"✅ Download complete! ({file_size_mb:.1f} MB)\n📤 Uploading...")
        
        # Split file if needed
        if file_size > TELEGRAM_FILE_LIMIT:
            await status_message.edit_text(f"📦 Large file, splitting...")
            chunks = split_file(video_path)
            
            for i, chunk in enumerate(chunks, 1):
                caption = f"Part {i}/{len(chunks)}" if len(chunks) > 1 else None
                with open(chunk, 'rb') as f:
                    await update.message.reply_document(
                        document=f,
                        filename=chunk.name,
                        caption=caption
                    )
                chunk.unlink()
            video_path.unlink(missing_ok=True)
        else:
            with open(video_path, 'rb') as f:
                await update.message.reply_video(
                    video=f,
                    filename=video_path.name,
                    supports_streaming=True
                )
            video_path.unlink(missing_ok=True)
        
        await status_message.edit_text("✅ Upload complete!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await status_message.edit_text(f"❌ Error: {str(e)}")
    
    finally:
        user_dir = DOWNLOAD_DIR / str(user_id)
        if user_dir.exists():
            shutil.rmtree(user_dir, ignore_errors=True)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors."""
    logger.error(f"Error: {context.error}", exc_info=context.error)


def main() -> None:
    """Start the bot."""
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is required")
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    application.add_error_handler(error_handler)
    
    logger.info("Bot started!")
    application.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
    main()