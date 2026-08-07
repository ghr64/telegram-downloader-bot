# YouTube Cookies Setup Guide

YouTube has increased bot detection and may require authentication for certain videos. This guide shows you how to export your YouTube cookies to bypass these restrictions.

## Why Do I Need Cookies?

Some videos show errors like:
- "Sign in to confirm you're not a bot"
- "Please sign in"
- Age-restricted content

Using cookies from your logged-in YouTube session solves these issues.

## Method 1: Browser Extension (Easiest)

### Chrome/Edge/Brave
1. Install [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
2. Go to [youtube.com](https://youtube.com) and sign in
3. Click the extension icon
4. Click "Export" → saves `cookies.txt` to Downloads
5. Upload this file to your server where the bot runs

### Firefox
1. Install [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)
2. Go to [youtube.com](https://youtube.com) and sign in
3. Click the extension icon → "Current Site"
4. Save the `cookies.txt` file
5. Upload to your server

## Method 2: Command Line (Advanced)

If you have `yt-dlp` installed locally:

```bash
# This opens a browser, you sign in, then it saves cookies
yt-dlp --cookies-from-browser chrome --cookies cookies.txt https://www.youtube.com/watch?v=dQw4w9WgXcQ

# Or from Firefox
yt-dlp --cookies-from-browser firefox --cookies cookies.txt https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

## How to Use Cookies with the Bot

### For VPS Deployment

1. Get `cookies.txt` using one of the methods above
2. Upload it to your server:
   ```bash
   # From your local machine
   scp cookies.txt user@your-server:/path/to/telegram-downloader-bot/cookies.txt
   ```
3. Restart the bot:
   ```bash
   sudo systemctl restart telegram-bot
   ```

### For Railway Deployment

Railway doesn't support file uploads directly. You need to:

#### Option A: Commit cookies to a private repo (recommended)
1. Make your GitHub repo **private** first
2. Add `cookies.txt` to your repo:
   ```bash
   cd /path/to/telegram-downloader-bot
   cp ~/Downloads/cookies.txt .
   git add cookies.txt
   git commit -m "Add YouTube authentication cookies"
   git push
   ```
3. Railway will redeploy with cookies

#### Option B: Base64 encode in environment variable
1. Encode your cookies:
   ```bash
   base64 -w 0 cookies.txt > cookies_encoded.txt
   ```
2. Add to Railway environment variables:
   - Variable: `YOUTUBE_COOKIES_BASE64`
   - Value: (paste the encoded string)
3. The bot will decode it on startup (requires code update)

## Security Notes

⚠️ **Important:** `cookies.txt` contains your YouTube session. Keep it private!

- Never commit cookies to a **public** GitHub repo
- Add `cookies.txt` to `.gitignore` if repo is public
- Cookies expire after ~6 months, you'll need to refresh them
- Don't share your cookies file with anyone

## Updating .gitignore

If your repo is public, make sure cookies aren't committed:

```bash
echo "cookies.txt" >> .gitignore
git add .gitignore
git commit -m "Ignore cookies file"
git push
```

## Testing

After adding cookies, test with a restricted video:

```
/start
# Then send a YouTube URL that previously failed
```

The bot will log: `Using cookies.txt for authentication` and should download successfully.

## Troubleshooting

### "Still getting sign-in errors"
- Cookies might be expired. Re-export from your browser
- Make sure you're logged into YouTube when exporting
- Try clearing YouTube cookies in browser and logging in again

### "cookies.txt not found"
- Check file path: should be in the same directory as `bot.py`
- Check file permissions: `chmod 644 cookies.txt`
- Check Railway logs to see if file is present

### "Video still won't download"
- Some videos are region-locked beyond cookies
- Try using a VPN on the server
- Some premium/members-only content can't be downloaded

## Cookie Format

Valid `cookies.txt` looks like this:
```
# Netscape HTTP Cookie File
.youtube.com	TRUE	/	TRUE	1234567890	CONSENT	YES+
.youtube.com	TRUE	/	FALSE	1234567890	VISITOR_INFO1_LIVE	xxx
```

If your file doesn't start with `# Netscape HTTP Cookie File`, it's the wrong format.

---

**Last Updated:** 2026-08-07
