import os
import json
import logging
import re

import motor.motor_asyncio
from discord.ext import commands

from utils.mongo import Document

with open("config.json", "r") as f:
    config = json.load(f)


async def get_prefix(bot, message):
    # If dm's
    if not message.guild:
        return commands.when_mentioned_or("py.")(bot, message)

    try:
        data = await bot.config.find(message.guild.id)

        # Make sure we have a useable prefix
        if not data or "prefix" not in data:
            return commands.when_mentioned_or("py.")(bot, message)
        return commands.when_mentioned_or(data["prefix"])(bot, message)
    except:
        return commands.when_mentioned_or("py.")(bot, message)


logging.basicConfig(level="INFO")
bot = commands.Bot(
    command_prefix=get_prefix,
    case_insensitive=True,
    description="A short sharp bot coded in python to aid the python developers with helping the community with discord.py related issues.",
)


# Use regex to parse mentions, much better than only supporting
# nickname mentions (<@!1234>)
# This basically ONLY matches a string that only consists of a mention
mention = re.compile(r"^<@!?(?P<id>\d+)>$")

logger = logging.getLogger(__name__)

bot.colors = {
    "WHITE": 0xFFFFFF,
    "AQUA": 0x1ABC9C,
    "GREEN": 0x2ECC71,
    "BLUE": 0x3498DB,
    "PURPLE": 0x9B59B6,
    "LUMINOUS_VIVID_PINK": 0xE91E63,
    "GOLD": 0xF1C40F,
    "ORANGE": 0xE67E22,
    "RED": 0xE74C3C,
    "NAVY": 0x34495E,
    "DARK_AQUA": 0x11806A,
    "DARK_GREEN": 0x1F8B4C,
    "DARK_BLUE": 0x206694,
    "DARK_PURPLE": 0x71368A,
    "DARK_VIVID_PINK": 0xAD1457,
    "DARK_GOLD": 0xC27C0E,
    "DARK_ORANGE": 0xA84300,
    "DARK_RED": 0x992D22,
    "DARK_NAVY": 0x2C3E50,
}
bot.color_list = [c for c in bot.colors.values()]
bot.menudocs_projects_id = config["menudocs_projects_id"]
bot.story_channel_id = config["story_channel_id"]
bot.dpy_help_channel_id = config["discord.py_help_channel"]

bot.remove_command("help")


@bot.event
async def on_ready():
    logger.info("I'm all up and ready like mom's spaghetti")

    # Database initialization
    bot.db = motor.motor_asyncio.AsyncIOMotorClient(config["mongo_url"]).pyro
    logger.info("Database connection established")

    bot.config = Document(bot.db, "config")


@bot.event
async def on_message(message):
    # Ignore messages sent by bots
    if message.author.bot:
        return

    # Whenever the bot is tagged, respond with its prefix
    if (match := mention.match(message.content)):
        if int(match.group("id")) == bot.user.id:
            data = await bot.config._Document__get_raw(message.guild.id)
            if not data or "prefix" not in data:
                prefix = "py."
            else:
                prefix = data["prefix"]
            await message.channel.send(f"My prefix here is `{prefix}`", delete_after=15)

    await bot.process_commands(message)


# Load all extensions
if __name__ == "__main__":
    for ext in os.listdir("./cogs/"):
        if ext.endswith(".py") and not ext.startswith("_"):
            try:
                bot.load_extension(f"cogs.{ext[:-3]}")
            except Exception as e:
                logger.error(
                    f"An error occured while loading extension: cogs.{ext[:-3]}, {repr(e)}"
                )

    bot.run(config["token"])
