# Telegram Video Downloader Bot

A powerful Telegram bot that downloads videos from YouTube, Instagram, and other platforms using yt-dlp. Automatically splits large files that exceed Telegram's size limits.

## Features

- 📥 Download videos from YouTube, Instagram, and many other platforms
- ✂️ Automatic file splitting for videos exceeding Telegram's 2GB limit
- 🎥 High-quality video downloads
- 📦 Clean, efficient file handling
- 🚀 Easy deployment to VPS or Railway

## Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (get from [@BotFather](https://t.me/botfather))

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/telegram-downloader-bot.git
cd telegram-downloader-bot
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your Telegram Bot Token:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### 5. Run the bot

```bash
python bot.py
```

## Usage

1. Start a chat with your bot on Telegram
2. Send `/start` to see the welcome message
3. Send any YouTube or Instagram URL
4. Wait for the bot to download and send the video

If the video is larger than 2GB, the bot will automatically split it into parts.

## Deployment

### VPS Deployment

1. **SSH into your VPS:**
   ```bash
   ssh user@your-vps-ip
   ```

2. **Install Python and dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv git -y
   ```

3. **Clone and setup:**
   ```bash
   git clone https://github.com/yourusername/telegram-downloader-bot.git
   cd telegram-downloader-bot
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   ```bash
   export TELEGRAM_BOT_TOKEN="your_token_here"
   ```

5. **Run with systemd (recommended for production):**

   Create a service file:
   ```bash
   sudo nano /etc/systemd/system/telegram-bot.service
   ```

   Add the following content:
   ```ini
   [Unit]
   Description=Telegram Video Downloader Bot
   After=network.target

   [Service]
   Type=simple
   User=your-username
   WorkingDirectory=/home/your-username/telegram-downloader-bot
   Environment="TELEGRAM_BOT_TOKEN=your_token_here"
   ExecStart=/home/your-username/telegram-downloader-bot/venv/bin/python bot.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable telegram-bot
   sudo systemctl start telegram-bot
   sudo systemctl status telegram-bot
   ```

### Railway Deployment

1. **Create a `railway.toml`** (already included in this repo)

2. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

3. **Deploy on Railway:**
   - Go to [Railway](https://railway.app)
   - Create a new project
   - Connect your GitHub repository
   - Add environment variable: `TELEGRAM_BOT_TOKEN`
   - Deploy!

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram Bot Token from @BotFather | Yes |

## Supported Platforms

This bot supports all platforms that yt-dlp supports, including:

- YouTube
- Instagram
- Facebook
- Twitter/X
- TikTok
- Vimeo
- Reddit
- And 1000+ more sites

## File Size Limits

- Telegram bot API has a 2GB file size limit
- Files larger than 2GB are automatically split into 1.9GB chunks
- Each chunk is sent as a separate document

## Troubleshooting

### Bot doesn't respond

- Check if the bot token is correct
- Verify the bot is running: `systemctl status telegram-bot` (on VPS with systemd)
- Check logs for errors

### Download fails

- Ensure the URL is valid and accessible
- Some platforms may require authentication or have regional restrictions
- Check yt-dlp is up to date: `pip install --upgrade yt-dlp`

### Out of disk space

- The bot automatically cleans up downloaded files after sending
- Ensure you have enough disk space for temporary downloads
- Large videos may require significant temporary storage

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Support

If you encounter any issues, please open an issue on GitHub.

## Credits

- Built with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- Powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp)
