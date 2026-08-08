#!/usr/bin/env python3
"""
Telegram YouTube/Instagram Downloader Bot
Downloads videos from YouTube and Instagram using yt-dlp
Automatically splits files that exceed Telegram's limits
"""

import os
import sys
import logging
import traceback
import shutil
import subprocess
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError

# Configure detailed logging
LOG_DIR = Path('./logs')
LOG_DIR.mkdir(exist_ok=True)

# Create timestamped log file
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = LOG_DIR / f'download_{timestamp}.log'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DOWNLOAD_DIR = Path('./downloads')
TELEGRAM_FILE_LIMIT = 2000 * 1024 * 1024  # 2GB limit for bots
CHUNK_SIZE = 1900 * 1024 * 1024  # 1.85GB per chunk (1900MB)

# Ensure download directory exists
DOWNLOAD_DIR.mkdir(exist_ok=True)


def format_error_details(error: Exception, context: Dict[str, Any]) -> str:
    """Format detailed error information for debugging."""
    error_info = {
        'timestamp': str(datetime.now()),
        'error_type': type(error).__name__,
        'error_message': str(error),
        'traceback': traceback.format_exc(),
        'context': context
    }
    
    # Add specific error details
    if hasattr(error, 'args') and error.args:
        error_info['args'] = error.args
    
    if isinstance(error, ExtractorError):
        error_info['extractor_error'] = {
            'expected': error.expected,
            'video_id': getattr(error, 'video_id', None)
        }
    
    if isinstance(error, DownloadError):
        error_info['download_error'] = True
    
    return json.dumps(error_info, indent=2, default=str)


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
    
    logger.info(f"File size {file_size} bytes exceeds limit. Splitting into {file_size // chunk_size + 1} chunks...")
    
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
            logger.info(f"Created chunk {chunk_num - 1}: {chunk_path.name} ({len(chunk_data)} bytes)")
    
    return chunks


def create_download_context(url: str, user_id: int, strategy_name: str) -> Dict[str, Any]:
    """Create debug context for download operations."""
    return {
        'url': url,
        'user_id': user_id,
        'download_dir': str(DOWNLOAD_DIR / str(user_id)),
        'strategy': strategy_name,
        'cookies_file': str(Path('./cookies.txt')) if Path('./cookies.txt').exists() else 'None',
        'timestamp': str(datetime.now())
    }


def download_video(url: str, user_id: int) -> Optional[Path]:
    """Download video using yt-dlp with multiple strategies and detailed logging."""
    user_download_dir = DOWNLOAD_DIR / str(user_id)
    user_download_dir.mkdir(exist_ok=True)
    
    output_template = str(user_download_dir / '%(title)s.%(ext)s')
    
    # Check for cookies file
    cookies_file = Path('./cookies.txt')
    logger.info(f"Cookies file exists: {cookies_file.exists()}")
    
    # Strategies in order of reliability
    strategies = [
        {'name': 'web_embedded', 'client': 'web_embedded', 'priority': 1},
        {'name': 'mweb', 'client': 'mweb', 'priority': 2},
        {'name': 'tv_embedded', 'client': 'tv_embedded', 'priority': 3},
        {'name': 'android_vr', 'client': 'android_vr', 'priority': 4},
        {'name': 'android', 'client': 'android', 'priority': 5},
        {'name': 'web_default', 'client': 'web,default', 'priority': 6},
    ]
    
    # Sort by priority
    strategies.sort(key=lambda x: x['priority'])
    
    logger.info(f"Starting download with {len(strategies)} strategies")
    logger.info(f"URL: {url}")
    logger.info(f"User ID: {user_id}")
    logger.info(f"Download directory: {user_download_dir}")
    
    errors_by_strategy = {}
    
    for strategy in strategies:
        strategy_name = strategy['name']
        logger.info(f"="*60)
        logger.info(f"Trying strategy {strategy_name} (priority: {strategy['priority']})")
        logger.info(f"="*60)
        
        context = create_download_context(url, user_id, strategy_name)
        context['strategy_priority'] = strategy['priority']
        
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best[height<=1080]/best',
            'outtmpl': output_template,
            'merge_output_format': 'mp4',
            'quiet': False,
            'verbose': True,  # Enable verbose output
            'cookiefile': str(cookies_file) if cookies_file.exists() else None,
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Sec-Fetch-Mode': 'navigate',
            },
            'retries': 3,
            'fragment_retries': 3,
            'extractor_args': {'youtube': {'player_client': [strategy['client']]}},
            'progress_hooks': [
            lambda d: logger.info(f"Progress: {d.get('status', 'unknown')} - {d.get('message', '')}")
        ],
            'postprocessor_hooks': [
            lambda d: logger.info(f"Post-processor: {d.get('status', 'unknown')}")
        ],
        }
        
        # Debug: log configuration
        logger.debug(f"yt-dlp options for {strategy_name}: {json.dumps(ydl_opts, indent=2, default=str)}")
        
        try:
            logger.info(f"Opening yt-dlp with options for {strategy_name}...")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Extracting info for: {url}")
                
                # Set up progress hooks for detailed logging
                def progress_hook(d):
                    status = d.get('status', 'unknown')
                    logger.info(f"Progress: {status} - {d.get('message', '')}")
                    
                    if status == 'error':
                        logger.error(f"Download error: {d.get('message', '')}")
                    elif status == 'downloading':
                        logger.info(f"Downloading... {d.get('download_current', 0)} / {d.get('download_total', 0)} bytes")
                    elif status == 'finished':
                        logger.info("Download complete!")
                
                ydl.add_progress_hook(progress_hook)
                
                info = ydl.extract_info(url, download=True)
                logger.info(f"Extraction complete for {strategy_name}")
                
                if info:
                    filename = ydl.prepare_filename(info)
                    logger.info(f"Prepared filename: {filename}")
                    
                    video_path = Path(filename)
                    
                    if video_path.exists():
                        file_size = video_path.stat().st_size
                        logger.info(f"Downloaded file exists: {video_path}")
                        logger.info(f"File size: {file_size} bytes ({file_size / (1024*1024):.2f} MB)")
                        
                        if file_size > 0:
                            logger.info(f"✅ SUCCESS: Download with strategy {strategy_name}")
                            return video_path
                        else:
                            logger.warning(f"Downloaded file is empty (0 bytes)")
                    else:
                        logger.warning(f"Downloaded file does not exist at expected path")
                        logger.warning(f"Files in download dir: {list(user_download_dir.glob('*'))}")
                    
        except ExtractorError as e:
            error_details = format_error_details(e, {**context, 'error_category': 'ExtractorError'})
            errors_by_strategy[strategy_name] = error_details
            logger.error(f"ExtractorError in {strategy_name}:\n{error_details}")
            
            # Check for bot detection
            if 'bot' in str(e).lower() or 'sign in' in str(e).lower():
                logger.error(f"🚨 BOT DETECTION DETECTED in strategy {strategy_name}")
            continue
            
        except DownloadError as e:
            error_details = format_error_details(e, {**context, 'error_category': 'DownloadError'})
            errors_by_strategy[strategy_name] = error_details
            logger.error(f"DownloadError in {strategy_name}:\n{error_details}")
            continue
            
        except Exception as e:
            error_details = format_error_details(e, {**context, 'error_category': type(e).__name__})
            errors_by_strategy[strategy_name] = error_details
            logger.error(f"Exception in {strategy_name}:\n{error_details}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            continue
        
        logger.info(f"Strategy {strategy_name} failed, trying next...")
    
    # All strategies failed - compile detailed error report
    logger.error("="*60)
    logger.error("ALL DOWNLOAD STRATEGIES FAILED")
    logger.error("="*60)
    
    error_report = {
        'summary': 'All strategies failed',
        'url': url,
        'user_id': user_id,
        'errors_by_strategy': errors_by_strategy,
        'timestamp': str(datetime.now()),
        'cookies_available': cookies_file.exists()
    }
    
    logger.error(f"\n{'='*60}")
    logger.error(f"ERROR REPORT:")
    logger.error(f"{'='*60}")
    for strategy, error in errors_by_strategy.items():
        logger.error(f"\n{strategy}:")
        logger.error(error)
    
    # Write error report to file
    error_file = LOG_DIR / f'error_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(error_file, 'w') as f:
        json.dump(error_report, f, indent=2, default=str)
    logger.info(f"Error report saved to: {error_file}")
    
    raise Exception(f"All download strategies failed. See logs for details. Error file: {error_file}")


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle URLs sent by users."""
    url = update.message.text.strip()
    user_id = update.effective_user.id
    
    logger.info(f"Received URL from user {user_id}: {url}")
    
    if not (url.startswith('http://') or url.startswith('https://')):
        await update.message.reply_text("❌ Please send a valid URL starting with http:// or https://")
        return
    
    status_message = await update.message.reply_text("⏳ Processing your request...\n📝 Starting download process...")
    
    try:
        await status_message.edit_text("📥 Downloading video...\n(Could take a while depending on video size)")
        
        video_path = download_video(url, user_id)
        
        if not video_path or not video_path.exists():
            logger.error("Download returned None or non-existent file")
            await status_message.edit_text(
                "❌ Download failed.\n\n"
                "Please check the logs for detailed error information."
            )
            return
        
        file_size = video_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        
        logger.info(f"Download successful: {video_path} ({file_size_mb:.1f} MB)")
        
        await status_message.edit_text(f"✅ Download complete! ({file_size_mb:.1f} MB)\n📤 Uploading to Telegram...")
        
        # Split file if needed
        if file_size > TELEGRAM_FILE_LIMIT:
            await status_message.edit_text(f"📦 Large file detected ({file_size_mb:.1f} MB)\n✂️ Splitting into 1.9GB chunks...")
            chunks = split_file(video_path)
            logger.info(f"Split into {len(chunks)} chunks")
            
            for i, chunk in enumerate(chunks, 1):
                caption = f"Part {i}/{len(chunks)}" if len(chunks) > 1 else None
                logger.info(f"Uploading chunk {i}/{len(chunks)}: {chunk.name}")
                with open(chunk, 'rb') as f:
                    await update.message.reply_document(
                        document=f,
                        filename=chunk.name,
                        caption=caption
                    )
                chunk.unlink()
            video_path.unlink(missing_ok=True)
        else:
            logger.info(f"Uploading video directly (under 2GB)")
            with open(video_path, 'rb') as f:
                await update.message.reply_video(
                    video=f,
                    filename=video_path.name,
                    supports_streaming=True
                )
            video_path.unlink(missing_ok=True)
        
        await status_message.edit_text("✅ Upload complete!")
        logger.info(f"Successfully completed for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error in handle_url for user {user_id}:\n{traceback.format_exc()}")
        
        # Get the latest error file if available
        error_files = list(LOG_DIR.glob('error_*.json'))
        error_file = error_files[-1] if error_files else None
        
        message = f"❌ Error: {str(e)}\n\n"
        if error_file:
            message += f"🔍 Debug info: {error_file.name}\n"
            message += f"Check /logs/{error_file.name} for details."
        
        try:
            await status_message.edit_text(message)
        except:
            await update.message.reply_text(message)
    
    finally:
        user_dir = DOWNLOAD_DIR / str(user_id)
        if user_dir.exists():
            shutil.rmtree(user_dir, ignore_errors=True)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error(f"Unhandled error in bot:\n{traceback.format_exc()}")
    logger.error(f"Error details: {context.error}")


def main() -> None:
    """Start the bot."""
    logger.info("="*60)
    logger.info("Starting Telegram Video Downloader Bot")
    logger.info("="*60)
    
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set!")
        raise ValueError("TELEGRAM_BOT_TOKEN is required")
    
    logger.info(f"Bot token configured: {TELEGRAM_BOT_TOKEN[:10]}...")
    logger.info(f"Log file: {log_file}")
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    application.add_error_handler(error_handler)
    
    logger.info("✅ Bot initialized successfully")
    logger.info("🚀 Starting polling...")
    
    application.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
    main()