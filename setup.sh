#!/bin/bash

# Telegram Video Downloader Bot - Setup Script for VPS

echo "🚀 Setting up Telegram Video Downloader Bot..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
echo "🐍 Installing Python and dependencies..."
sudo apt install python3 python3-pip python3-venv git ffmpeg -y

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python packages
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your TELEGRAM_BOT_TOKEN"
    echo "   Run: nano .env"
    echo ""
fi

# Create downloads directory
mkdir -p downloads

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file: nano .env"
echo "2. Add your bot token from @BotFather"
echo "3. Run the bot: python bot.py"
echo ""
echo "Or set up as a systemd service for production (see README.md)"
