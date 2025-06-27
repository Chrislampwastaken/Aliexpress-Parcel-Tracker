# Aliexpress/Cainiao Discord Parcel Tracker

![GitHub](https://img.shields.io/badge/Python-3.8%2B-blue)
![GitHub](https://img.shields.io/badge/license-MIT-green)

A Discord bot that automatically tracks Aliexpress packages via Cainiao and other carriers, posting updates to your channel without manual checking.

## Features ✨

- **Automatic Tracking**: Updates every 10 minutes
- **Simple Commands**: Easy-to-use Discord interface

## Installation 🛠️

### Prerequisites
- Python 3.8+
- pip package manager
- Discord bot token ([how to create](https://discordpy.readthedocs.io/en/stable/discord.html))

### Setup
# Clone the repository
```bash
git clone https://github.com/Chrislampwastaken/Aliexpress-Parcel-Tracker.git
cd Aliexpress-Parcel-Tracker
```

# Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
```

# Install dependencies
```bash
pip install discord.py aiohttp python-dotenv
```

# Configuration
Create a .env file:
```bash
DISCORD_TOKEN=your_bot_token_here
DEFAULT_CHANNEL_ID=your_channel_id_here
```

# Usage
Run the script:
```bash
python bot.py
```
Might need to use python3 instead of python

# Running in the background
```bash
# Using screen (Linux/Mac)
screen -S tracker
python bot.py
# Press Ctrl+A then D to detach

# To resume:
screen -r tracker
```

# Commands 
Command	Description	Example
```bash
!track <ID>  Start tracking a package	ie !track LP123456789CN
!remove <ID>	Stop tracking a package	ie !remove LP123456789CN
!checkperms	Verify bot permissions	ie !checkperms
```

# To do
- Docker container support
- Expanded carrier support (USPS, DHL, etc.)
- Headless mode

# Comments
This is my first ever project that I ever finished. I am quite proud of how well it works compared to my skills.
