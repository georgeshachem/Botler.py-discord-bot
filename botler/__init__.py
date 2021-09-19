import discord
from discord.ext import commands
import traceback
import botler.utils
from pathlib import Path

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=botler.utils.get_prefix,
                   description=botler.utils.config.description,
                   intents=intents)


def extensions():
    files = Path("botler", "cogs").rglob("*.py")
    for file in files:
        yield file.as_posix()[:-3].replace("/", ".")


def load_extensions(_bot):
    for ext in extensions():
        print("Loaded ", ext)
        try:
            _bot.load_extension(ext)
        except (discord.ClientException, ModuleNotFoundError):
            print(f'Failed to load extension {ext}.')
            traceback.print_exc()


def run():
    load_extensions(bot)
    bot.run(botler.utils.config.token)