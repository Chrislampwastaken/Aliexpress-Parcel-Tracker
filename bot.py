import discord
from discord.ext import commands, tasks
import logging
import os
import json
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DEFAULT_CHANNEL_ID = int(os.getenv("DEFAULT_CHANNEL_ID"))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JSON file to store tracked numbers
TRACKED_FILE = "tracked.json"

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

tracked = {}  # {tracking_number: {"last_status": str, "channel_id": int}}

def save_tracked():
    try:
        with open(TRACKED_FILE, "w") as f:
            json.dump(tracked, f)
        logger.info("Tracked data saved.")
    except Exception as e:
        logger.error(f"Error saving tracked data: {e}")

def load_tracked():
    global tracked
    try:
        with open(TRACKED_FILE, "r") as f:
            tracked.update(json.load(f))
        logger.info("Tracked data loaded.")
    except FileNotFoundError:
        logger.info("No tracked.json found, starting fresh.")
    except Exception as e:
        logger.error(f"Error loading tracked data: {e}")

class CainiaoTracker:
    @staticmethod
    async def get_package_info(tracking_number):
        headers = {
            "accept": "application/json, text/plain, */*",
            "user-agent": "Mozilla/5.0",
            "referer": f"https://global.cainiao.com/newDetail.htm?mailNoList={tracking_number}"
        }
        url = f"https://global.cainiao.com/global/detail.json?mailNos={tracking_number}&lang=en-US"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as resp:
                    resp.raise_for_status()
                    return await resp.json()
        except Exception as e:
            logger.error(f"API Error: {e}")
            return None

@bot.command()
async def checkperms(ctx):
    perms = ctx.channel.permissions_for(ctx.guild.me)
    message = (
        "**Bot Permissions:**\n"
        f"✅ Send Messages: {perms.send_messages}\n"
        f"✅ Embed Links: {perms.embed_links}\n"
        f"✅ Read History: {perms.read_message_history}\n"
        f"**Channel:** #{ctx.channel.name}"
    )
    try:
        await ctx.send(message)
    except:
        logger.error("Couldn't send permission check")

@bot.command()
async def track(ctx, tracking_number: str):
    """Track a new package"""
    try:
        if not ctx.channel.permissions_for(ctx.guild.me).send_messages:
            await ctx.author.send("❌ I can't send messages in that channel!")
            return

        data = await CainiaoTracker.get_package_info(tracking_number)
        if not data or not data.get('module'):
            await ctx.send("⚠️ Couldn't fetch tracking data. Check the number or try later.")
            return

        info = data['module'][0]
        latest = info['latestTrace']
        status = f"{latest['timeStr']}: {latest['desc']}"

        tracked[tracking_number] = {
            "last_status": status,
            "channel_id": ctx.channel.id
        }
        save_tracked()

        perms = ctx.channel.permissions_for(ctx.guild.me)
        if perms.embed_links:
            embed = discord.Embed(
                title=f"📦 Tracking #{tracking_number}",
                color=0x00ff00
            )
            embed.add_field(name="Status", value=info['statusDesc'], inline=True)
            embed.add_field(name="Location", value=latest['desc'], inline=True)
            embed.add_field(name="Last Update", value=latest['timeStr'], inline=False)
            embed.add_field(name="Route", value=f"{info['originCountry']} → {info['destCountry']}", inline=False)
            await ctx.send(embed=embed)
        else:
            message = (
                f"**Tracking #{tracking_number}**\n"
                f"**Status:** {info['statusDesc']}\n"
                f"**Location:** {latest['desc']}\n"
                f"**Last Update:** {latest['timeStr']}\n"
                f"**Route:** {info['originCountry']} → {info['destCountry']}"
            )
            await ctx.send(message)

        await ctx.send(f"✅ Now tracking package. Updates every 10 minutes.")
    except Exception as e:
        logger.error(f"Track command error: {e}")
        await ctx.send("⚠️ An error occurred. Use !checkperms to verify my permissions.")

@bot.command()
async def remove(ctx, tracking_number: str):
    """Stop tracking a package"""
    if not ctx.channel.permissions_for(ctx.guild.me).send_messages:
        await ctx.author.send("❌ I can't send messages in that channel!")
        return

    if tracking_number in tracked:
        del tracked[tracking_number]
        save_tracked()
        await ctx.send(f"✅ Stopped tracking {tracking_number}.")
    else:
        await ctx.send(f"⚠️ That tracking number was not being tracked.")

@tasks.loop(minutes=10)
async def check_updates():
    for tracking_number, info in list(tracked.items()):
        try:
            channel = bot.get_channel(info['channel_id'])
            if not channel:
                continue

            data = await CainiaoTracker.get_package_info(tracking_number)
            if not data or not data.get('module'):
                continue

            new_info = data['module'][0]
            new_latest = new_info['latestTrace']
            new_status = f"{new_latest['timeStr']}: {new_latest['desc']}"

            if info['last_status'] != new_status:
                tracked[tracking_number]['last_status'] = new_status
                save_tracked()

                perms = channel.permissions_for(channel.guild.me)
                if not perms.send_messages:
                    continue

                if perms.embed_links:
                    embed = discord.Embed(
                        title=f"📦 Update for #{tracking_number}",
                        color=0xffa500
                    )
                    embed.add_field(name="New Status", value=new_info['statusDesc'], inline=True)
                    embed.add_field(name="Location", value=new_latest['desc'], inline=True)
                    embed.add_field(name="Time", value=new_latest['timeStr'], inline=False)
                    await channel.send(embed=embed)
                else:
                    message = (
                        f"**Update for #{tracking_number}**\n"
                        f"**New Status:** {new_info['statusDesc']}\n"
                        f"**Location:** {new_latest['desc']}\n"
                        f"**Time:** {new_latest['timeStr']}"
                    )
                    await channel.send(message)

        except Exception as e:
            logger.error(f"Update check error for {tracking_number}: {e}")

@bot.event
async def on_ready():
    load_tracked()
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    check_updates.start()
    # optional welcome message to default channel
    channel = bot.get_channel(DEFAULT_CHANNEL_ID)
    if channel:
        try:
            await channel.send("🤖 Tracker bot online and ready!")
        except:
            logger.warning("Couldn't send welcome message to default channel.")

bot.run(DISCORD_TOKEN)

