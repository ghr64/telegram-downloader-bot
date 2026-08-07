#!/usr/bin/env python3
"""
Telegram YouTube/Instagram Downloader Bot
Downloads videos from YouTube and Instagram using yt-dlp
Automatically splits files that exceed Telegram's limits
"""

import os
import logging
import asyncio
from pathlib import Path
from typing import Optional, List
import shutil
import subprocess

from telegram import Update, Message
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from telegram.constants import ParseMode
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


async def check_video_height(video_path: Path) -> Optional[int]:
    """Check video height using ffprobe."""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0', 
             '-show_entries', 'stream=height', '-of', 'csv=p=0', str(video_path)],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip().isdigit():
            return int(result.stdout.strip())
    except Exception:
        pass
    return None


async def download_video(url: str, user_id: int) -> Optional[Path]:
    """Download video using yt-dlp with advanced bot detection bypass."""
    user_download_dir = DOWNLOAD_DIR / str(user_id)
    user_download_dir.mkdir(exist_ok=True)
    
    output_template = str(user_download_dir / '%(title)s.%(ext)s')
    
    # Check for cookies file
    cookies_file = Path('./cookies.txt')
    
    # Define multiple download strategies (fallback chain)
    # Based on proven GitHub Actions workflow techniques
    strategies = [
        # Strategy 1: Web client + Deno JS solver + remote EJS (best for challenges)
        {
            'name': 'web+deno+ejs_github',
            'extractor_args': {'youtube': {'player_client': ['web']}},
            'js_runtimes': ['deno'],
            'remote_components': ['ejs:github'],
        },
        # Strategy 2: Web client + Deno + EJS via NPM
        {
            'name': 'web+deno+ejs_npm',
            'extractor_args': {'youtube': {'player_client': ['web']}},
            'js_runtimes': ['deno'],
            'remote_components': ['ejs:npm'],
        },
        # Strategy 3: Multiple clients combined + Deno + EJS
        {
            'name': 'web_mweb_android_vr+deno+ejs',
            'extractor_args': {'youtube': {'player_client': ['web', 'mweb', 'android_vr']}},
            'js_runtimes': ['deno'],
            'remote_components': ['ejs:github'],
        },
        # Strategy 4: mweb client (mobile web)
        {
            'name': 'mweb',
            'extractor_args': {'youtube': {'player_client': ['mweb']}},
            'js_runtimes': None,
            'remote_components': None,
        },
        # Strategy 5: Android VR client
        {
            'name': 'android_vr',
            'extractor_args': {'youtube': {'player_client': ['android_vr']}},
            'js_runtimes': None,
            'remote_components': None,
        },
        # Strategy 6: Web client no-proxy + Deno + EJS
        {
            'name': 'web+deno+ejs_noproxy',
            'extractor_args': {'youtube': {'player_client': ['web']}},
            'js_runtimes': ['deno'],
            'remote_components': ['ejs:github'],
        },
        # Strategy 7: mweb no-proxy
        {
            'name': 'mweb_noproxy',
            'extractor_args': {'youtube': {'player_client': ['mweb']}},
            'js_runtimes': None,
            'remote_components': None,
        },
        # Strategy 8: Android client (last resort, lower quality)
        {
            'name': 'android_fallback',
            'extractor_args': {'youtube': {'player_client': ['android']}},
            'js_runtimes': None,
            'remote_components': None,
        },
    ]
    
    # Common base options
    base_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_template,
        'merge_output_format': 'mp4',
        'quiet': False,
        'no_warnings': False,
        'progress_hooks': [],
        'age_limit': None,
        'geo_bypass': True,
        'geo_bypass_country': 'US',
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Sec-Fetch-Mode': 'navigate',
        },
        'retries': 5,
        'fragment_retries': 5,
        'no_check_certificates': True,
        'concurrent_fragments': 8,
        'buffer_size': '16K',
        'http_chunk_size': '10M',
        'no_part': True,
        'no_playlist': True,
    }
    
    # Add cookies if file exists
    if cookies_file.exists():
        base_opts['cookiefile'] = str(cookies_file)
        logger.info("Using cookies.txt for authentication")
    
    last_error = None
    
    # Try each strategy until one works
    for i, strategy in enumerate(strategies, 1):
        strategy_name = strategy['name']
        logger.info(f"Trying download strategy {i}/8: {strategy_name}")
        
        # Build options for this strategy
        ydl_opts = base_opts.copy()
        ydl_opts.update(strategy['extractor_args'])
        
        if strategy['js_runtimes']:
            ydl_opts['js_runtimes'] = strategy['js_runtimes']
        if strategy['remote_components']:
            ydl_opts['remote_components'] = strategy['remote_components']
        
        # Add strategy-specific user agent
        if strategy_name == 'android_fallback':
            ydl_opts['headers']['User-Agent'] = 'Mozilla/5.0 (Linux; Android 12; SM-S906N Build/QP1A.190711.020) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36'
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Downloading from: {url} using {strategy_name}")
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                video_path = Path(filename)
                
                # Verify quality for non-best strategies
                if video_path.exists() and video_path.stat().st_size > 0:
                    # Check actual video height
                    height = await check_video_height(video_path)
                    if height:
                        logger.info(f"Downloaded video height: {height}px")
                        # For 'best' quality, reject if only 360p (sign of failed challenge)
                        if height <= 360 and i < 8:
                            logger.warning(f"Strategy {strategy_name} only got {height}p, trying next strategy...")
                            video_path.unlink(missing_ok=True)
                            continue
                    
                    logger.info(f"✅ Download successful with strategy: {strategy_name}")
                    return video_path
                    
        except Exception as e:
            last_error = e
            logger.warning(f"Strategy {strategy_name} failed: {e}")
            # Clean up any partial files
            for partial in user_download_dir.glob('*.part'):
                partial.unlink(missing_ok=True)
            await asyncio.sleep(2)  # Brief delay between strategies
            continue
    
    # All strategies failed
    logger.error(f"All 8 download strategies failed. Last error: {last_error}")
    raise last_error or Exception("All download strategies failed")


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle URLs sent by users."""
    url = update.message.text.strip()
    user_id = update.effective_user.id
    
    # Check if it looks like a URL
    if not (url.startswith('http://') or url.startswith('https://')):
        await update.message.reply_text(
            "❌ Please send a valid URL starting with http:// or https://"
        )
        return
    
    # Send initial status
    status_message = await update.message.reply_text(
        "⏳ Processing your request...\n"
        "📥 Starting download..."
    )
    
    try:
        # Download the video
        await status_message.edit_text(
            "⏳ Downloading video...\n"
            "This may take a while depending on the video size.\n"
            "🔄 Trying multiple strategies to bypass bot detection..."
        )
        
        video_path = await download_video(url, user_id)
        
        if not video_path or not video_path.exists():
            await status_message.edit_text("❌ Download failed. Please try again.")
            return
        
        # Check file size and split if necessary
        file_size = video_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        
        await status_message.edit_text(
            f"✅ Download complete! ({file_size_mb:.2f} MB)\n"
            f"📤 Uploading to Telegram..."
        )
        
        # Split file if needed
        if file_size > TELEGRAM_FILE_LIMIT:
            await status_message.edit_text(
                f"📦 File is large ({file_size_mb:.2f} MB)\n"
                f"✂️ Splitting into parts..."
            )
            chunks = split_file(video_path)
            
            await status_message.edit_text(
                f"📤 Uploading {len(chunks)} parts..."
            )
            
            for i, chunk in enumerate(chunks, 1):
                caption = f"Part {i}/{len(chunks)}" if len(chunks) > 1 else None
                
                with open(chunk, 'rb') as f:
                    await update.message.reply_document(
                        document=f,
                        filename=chunk.name,
                        caption=caption
                    )
                
                # Clean up chunk
                chunk.unlink()
            
            # Clean up original file
            video_path.unlink()
            
        else:
            # Send as video if under limit
            with open(video_path, 'rb') as f:
                await update.message.reply_video(
                    video=f,
                    filename=video_path.name,
                    supports_streaming=True
                )
            
            # Clean up
            video_path.unlink()
        
        await status_message.edit_text("✅ Upload complete!")
        
    except Exception as e:
        logger.error(f"Error processing URL: {e}", exc_info=True)
        await status_message.edit_text(
            f"❌ Error: {str(e)}\n\n"
            "Please make sure the URL is valid and the video is accessible."
        )
    
    finally:
        # Clean up user directory
        user_dir = DOWNLOAD_DIR / str(user_id)
        if user_dir.exists():
            shutil.rmtree(user_dir, ignore_errors=True)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)


def main() -> None:
    """Start the bot."""
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set!")
    
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()