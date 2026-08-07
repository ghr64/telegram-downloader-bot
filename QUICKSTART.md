# Quick Start Guide

## Getting Your Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot`
3. Choose a name for your bot (e.g., "My Video Downloader")
4. Choose a username (must end in 'bot', e.g., "my_video_downloader_bot")
5. Copy the token BotFather gives you

## Local Testing

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/telegram-downloader-bot.git
cd telegram-downloader-bot

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your bot token
export TELEGRAM_BOT_TOKEN="your_token_here"  # Windows: set TELEGRAM_BOT_TOKEN=your_token_here

# 5. Run the bot
python bot.py
```

## VPS Deployment (Ubuntu/Debian)

```bash
# 1. SSH into your VPS
ssh user@your-vps-ip

# 2. Clone the repository
git clone https://github.com/yourusername/telegram-downloader-bot.git
cd telegram-downloader-bot

# 3. Run setup script
chmod +x setup.sh
./setup.sh

# 4. Edit .env file
nano .env
# Add your token: TELEGRAM_BOT_TOKEN=your_token_here

# 5. Test the bot
source venv/bin/activate
python bot.py

# 6. Set up as a service (production)
sudo cp telegram-bot.service /etc/systemd/system/
sudo nano /etc/systemd/system/telegram-bot.service
# Update: User, WorkingDirectory, ExecStart paths, and TELEGRAM_BOT_TOKEN

sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot

# View logs
sudo journalctl -u telegram-bot -f
```

## Railway Deployment

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/telegram-downloader-bot.git
   git push -u origin main
   ```

2. **Deploy on Railway:**
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Add environment variable:
     - Key: `TELEGRAM_BOT_TOKEN`
     - Value: Your bot token from BotFather
   - Railway will automatically detect the `railway.toml` and deploy
   - Click "Deploy"

3. **Monitor:**
   - Check logs in Railway dashboard
   - Your bot should be online within 1-2 minutes

## Testing Your Bot

1. Open Telegram
2. Search for your bot username
3. Send `/start`
4. Send a YouTube URL (e.g., `https://www.youtube.com/watch?v=dQw4w9WgXcQ`)
5. Wait for download and upload

## Troubleshooting

**Bot not responding:**
- Verify token is correct
- Check bot is running: `systemctl status telegram-bot`
- Check logs: `sudo journalctl -u telegram-bot -f`

**Download fails:**
- Ensure ffmpeg is installed: `sudo apt install ffmpeg`
- Update yt-dlp: `pip install --upgrade yt-dlp`
- Check URL is valid and publicly accessible

**Out of memory:**
- Large videos need temporary storage
- Check disk space: `df -h`
- Consider upgrading VPS or Railway plan

## Supported URLs

Test with these platforms:
- YouTube: `https://www.youtube.com/watch?v=...`
- YouTube Shorts: `https://www.youtube.com/shorts/...`
- Instagram: `https://www.instagram.com/p/...`
- Instagram Reels: `https://www.instagram.com/reel/...`
- Twitter/X: `https://twitter.com/.../status/...`
- TikTok: `https://www.tiktok.com/@.../video/...`
- Facebook: `https://www.facebook.com/.../videos/...`

## Next Steps

- Star the repo if you find it useful!
- Report issues on GitHub
- Contribute improvements via Pull Requests
