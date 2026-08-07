# Deployment Checklist

Use this checklist when deploying your bot to ensure everything is configured correctly.

## ✅ Pre-Deployment

- [ ] Python 3.8+ installed
- [ ] Git installed
- [ ] Bot token obtained from @BotFather
- [ ] Repository cloned/downloaded

## ✅ Local Testing Checklist

- [ ] Virtual environment created (`python3 -m venv venv`)
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Environment variable set (`export TELEGRAM_BOT_TOKEN="..."`)
- [ ] Bot runs without errors (`python bot.py`)
- [ ] Bot responds to `/start` command
- [ ] Bot downloads a test YouTube video
- [ ] Bot uploads video successfully
- [ ] Files cleaned up after upload

## ✅ VPS Deployment Checklist

### Initial Setup
- [ ] SSH access to VPS confirmed
- [ ] VPS has Ubuntu/Debian OS
- [ ] System packages updated (`sudo apt update && sudo apt upgrade`)
- [ ] Python 3.8+ installed (`python3 --version`)
- [ ] Git installed (`git --version`)
- [ ] FFmpeg installed (`ffmpeg -version`)

### Application Setup
- [ ] Repository cloned to VPS
- [ ] Setup script executed (`./setup.sh`)
- [ ] `.env` file created and configured
- [ ] Bot token added to `.env`
- [ ] Virtual environment activated
- [ ] Bot runs successfully in foreground test

### Service Configuration
- [ ] `telegram-bot.service` file edited with correct paths
- [ ] Username updated in service file
- [ ] Working directory path updated
- [ ] ExecStart path updated with absolute path
- [ ] Bot token added to service file
- [ ] Service file copied to `/etc/systemd/system/`
- [ ] Systemd daemon reloaded (`sudo systemctl daemon-reload`)
- [ ] Service enabled (`sudo systemctl enable telegram-bot`)
- [ ] Service started (`sudo systemctl start telegram-bot`)
- [ ] Service status is active (`sudo systemctl status telegram-bot`)

### Verification
- [ ] Bot responds to Telegram messages
- [ ] Logs are clean (`sudo journalctl -u telegram-bot -f`)
- [ ] Test download completes successfully
- [ ] Files are cleaned up automatically
- [ ] Service restarts automatically after reboot

### Security (Optional but Recommended)
- [ ] Firewall configured (`ufw allow 22/tcp`)
- [ ] Fail2ban installed for SSH protection
- [ ] Non-root user created for running bot
- [ ] Bot token stored securely (not in git)
- [ ] Logs rotation configured

## ✅ Railway Deployment Checklist

### Repository Setup
- [ ] Code pushed to GitHub
- [ ] `.gitignore` prevents `.env` from being committed
- [ ] `railway.toml` exists in root directory
- [ ] `requirements.txt` is up to date

### Railway Configuration
- [ ] Railway account created
- [ ] New project created
- [ ] GitHub repository connected
- [ ] Environment variable `TELEGRAM_BOT_TOKEN` added
- [ ] Deployment triggered

### Verification
- [ ] Build logs show successful installation
- [ ] Application starts without errors
- [ ] Bot responds to Telegram messages
- [ ] Test download works
- [ ] Logs accessible in Railway dashboard

### Monitoring
- [ ] Check resource usage (RAM/CPU)
- [ ] Monitor for crashes in logs
- [ ] Verify automatic restarts work
- [ ] Test with large files (>100MB)

## ✅ GitHub Publication Checklist

### Before Publishing
- [ ] Remove any test tokens from code
- [ ] `.env.example` created (without real token)
- [ ] `.gitignore` includes `.env`
- [ ] README.md is complete
- [ ] LICENSE file included
- [ ] Code comments are clear
- [ ] No sensitive data in commit history

### Repository Setup
- [ ] Repository created on GitHub
- [ ] Repository name chosen
- [ ] Description added
- [ ] Topics/tags added (telegram, bot, downloader, python)
- [ ] README displays correctly
- [ ] License selected

### First Commit
- [ ] All files added (`git add .`)
- [ ] Meaningful commit message
- [ ] Pushed to main branch
- [ ] All files visible on GitHub

### Post-Publication
- [ ] README renders correctly
- [ ] Installation instructions tested
- [ ] Links in README work
- [ ] Example commands are accurate
- [ ] Consider adding screenshots/demo

## 🧪 Testing Checklist

### Basic Functionality
- [ ] Bot starts without errors
- [ ] `/start` command works
- [ ] `/help` command works
- [ ] URL validation works (rejects invalid URLs)

### Download Testing
- [ ] YouTube video downloads
- [ ] YouTube Shorts downloads
- [ ] Instagram post downloads
- [ ] Instagram Reel downloads
- [ ] Twitter/X video downloads (if supported)

### File Size Testing
- [ ] Small file (<50MB) uploads as video
- [ ] Medium file (500MB-1GB) uploads successfully
- [ ] Large file (>2GB) splits correctly
- [ ] All parts upload successfully
- [ ] Files cleanup after upload

### Error Handling
- [ ] Invalid URL shows error message
- [ ] Private video shows appropriate error
- [ ] Network error handled gracefully
- [ ] Disk full error logged properly

## 📊 Performance Checklist

- [ ] Bot response time < 2 seconds
- [ ] Downloads don't timeout
- [ ] Memory usage stays reasonable
- [ ] No memory leaks over 24 hours
- [ ] Concurrent downloads handled (if multiple users)

## 🔧 Maintenance Checklist

### Weekly
- [ ] Check bot is still running
- [ ] Review error logs
- [ ] Check disk space

### Monthly
- [ ] Update yt-dlp (`pip install --upgrade yt-dlp`)
- [ ] Update python-telegram-bot if needed
- [ ] Review and clear old logs
- [ ] Test with current video URLs

### As Needed
- [ ] Update documentation if features change
- [ ] Respond to GitHub issues
- [ ] Review pull requests
- [ ] Update Python version if security patches released

## 🚨 Troubleshooting Checklist

If bot not working:
- [ ] Check bot token is correct
- [ ] Verify bot process is running
- [ ] Check logs for errors
- [ ] Verify internet connectivity
- [ ] Check disk space available
- [ ] Restart bot service
- [ ] Check yt-dlp is up to date
- [ ] Test with known working URL

## ✨ Success Criteria

Your deployment is successful when:
- [ ] Bot responds to commands instantly
- [ ] Downloads complete successfully
- [ ] Files upload without errors
- [ ] Large files split and upload correctly
- [ ] Temporary files are cleaned up
- [ ] Bot stays online 24/7
- [ ] Error messages are user-friendly
- [ ] Logs show no critical errors

---

**Note:** This checklist is comprehensive. Not all items may apply to your specific deployment scenario.

**Date Created:** 2026-08-07
**Last Updated:** 2026-08-07
