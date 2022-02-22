import discord
from discord.ext import commands
import traceback
import botler.utils
from pathlib import Path
import botler.database.models as models

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=botler.utils.get_prefix,
                   description=botler.utils.config.description,
                   intents=intents,
                   help_command=None)


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


@bot.event
async def on_message(message):
    if ((message.guild) and (not message.author.bot)):
        member_balance = await models.Economy.query.where((models.Economy.guild_id == message.guild.id) & (models.Economy.member_id == message.author.id)).gino.first()
        if (member_balance):
            await member_balance.update(balance=member_balance.balance+2).apply()
        else:
            await models.Economy.create(guild_id=message.guild.id, member_id=message.author.id)

    await bot.process_commands(message)


def run():
    load_extensions(bot)
    bot.run(botler.utils.config.token)
