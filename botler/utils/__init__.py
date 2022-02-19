from botler.database.models import Guild
from discord.ext import commands
from .config import Config

config = Config()


async def preload_guild_data():
    guilds = await Guild.query.gino.all()
    d = dict()
    for guild in guilds:
        d[guild.id] = {"prefix": guild.prefix}
    return d


def get_guild_prefix(bot, guild_id):
    guild_data = bot.guild_data.get(guild_id, None)
    if guild_data is not None:
        return guild_data.get("prefix")
    else:
        return config.prefix


async def get_prefix(bot, message):
    if not message.guild:
        prefix = config.prefix
    else:
        prefix = get_guild_prefix(bot, message.guild.id)
    return commands.when_mentioned_or(prefix)(bot, message)
