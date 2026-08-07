# Final Setup - YouTube Cookies Configuration

## ✅ You're All Set!

Your Telegram bot is ready to download videos. The YouTube cookies have been added locally to bypass bot detection.

## 📍 Local Setup (VPS/Railway)

### Step 1: Add Your Cookies
Place your `cookies.txt` file in the bot directory:
```bash
# Copy your cookies.txt to the bot root
cp ~/cookies.txt /path/to/telegram-downloader-bot/cookies.txt
```

**File location:** `/opt/data/telegram-downloader-bot/cookies.txt`

### Step 2: Deploy on Railway

Railway will **NOT see cookies.txt** (it's in `.gitignore` for security). To use cookies on Railway:

**Option A: Private GitHub Repo** (Recommended)
1. Make your GitHub repo private
2. Commit cookies: `git add cookies.txt -f && git commit -m "Add cookies"`
3. Push to private repo
4. Railway will use cookies automatically

**Option B: Environment Variable**
1. Encode cookies: `base64 cookies.txt > encoded.txt`
2. Add Railway env var: `YOUTUBE_COOKIES_BASE64` = (paste base64 content)
3. Bot decodes and uses them on startup

### Step 3: Test Locally

```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set bot token
export TELEGRAM_BOT_TOKEN="your_token_here"

# Run bot
python bot.py
```

Send a test URL to your bot:
```
https://www.youtube.com/watch?v=peKFHc-Jtto
```

## 🔑 What's Working Now

✅ **Bot Detection Bypass** - Uses `player_client=['default', 'web_embedded']`
✅ **YouTube Cookies** - Session authentication included
✅ **Browser Headers** - Looks like real Chrome browser
✅ **Auto File Splitting** - Handles videos >2GB
✅ **Railway Ready** - NIXPACKS build config included
✅ **VPS Ready** - Systemd service template included

## 🚀 Deploy Command

### Railway (Automatic)
```bash
# Push to GitHub, Railway auto-deploys
git push origin main
```

### VPS (Manual)
```bash
# 1. Clone repo
git clone https://github.com/ghr64/telegram-downloader-bot.git
cd telegram-downloader-bot

# 2. Copy cookies
cp ~/cookies.txt .

# 3. Setup
./setup.sh

# 4. Start service
sudo systemctl start telegram-bot
sudo systemctl enable telegram-bot
```

## 📋 Files Structure

```
telegram-downloader-bot/
├── bot.py                    # Main bot (with cookie support)
├── requirements.txt          # Dependencies
├── cookies.txt              # Your YouTube cookies (local only)
├── .gitignore               # Excludes cookies from git
├── railway.toml             # Railway deployment config
├── setup.sh                 # VPS setup script
├── telegram-bot.service     # Systemd service
├── README.md                # Full documentation
├── COOKIES_SETUP.md         # How to export cookies
├── DEPLOYMENT_CHECKLIST.md  # Deployment guide
└── LICENSE                  # MIT License
```

## 🔒 Security Notes

- `cookies.txt` is **NOT in git** (protected by .gitignore)
- If repo is **private**, you CAN commit cookies
- If repo is **public**, keep cookies locally only
- Cookies expire every ~6 months, re-export as needed

## ❌ If Bot Still Says "Sign in to confirm you're not a bot"

1. **Refresh cookies** - Export new cookies from YouTube
2. **Update bot** - Pull latest code: `git pull`
3. **Check Railway logs** - Verify cookies were loaded
4. **Try different video** - Some videos are heavily restricted

## 📞 Support

- **Issue:** Video won't download
  - Try with a different public YouTube video first
  - Check cookies are fresh (not expired)
  - Verify bot token is correct

- **Issue:** Railway deployment fails
  - Check environment variable `TELEGRAM_BOT_TOKEN` is set
  - View Railway logs: Dashboard → Deployments → Logs

- **Issue:** VPS systemd service won't start
  - Check logs: `sudo journalctl -u telegram-bot -f`
  - Verify paths in service file are absolute
  - Check permissions: `ls -la telegram-bot.service`

---

**Bot Status:** ✅ Ready to Deploy
**Last Updated:** 2026-08-07
**Repository:** https://github.com/ghr64/telegram-downloader-bot
