import discord
from discord.ext import commands
import botler.database as db
import botler.utils

invite_link = "https://discord.com/api/oauth2/authorize?client_id={}&&permissions=8&scope=bot"


class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await db.setup()
        self.bot.guild_data = await botler.utils.preload_guild_data()
        self.bot.invite = invite_link.format(self.bot.user.id)
        print('-----------------------')
        print('Logged in as')
        print(self.bot.user.name)
        print(self.bot.user.id)
        print('-----------------------')
        game = discord.Game(
            name="&help | {} servers".format(len(self.bot.guilds)))
        await self.bot.change_presence(activity=game)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        guild_id = int(guild.id)
        await db.query_guild(guild_id)
        self.bot.guild_data[guild_id] = botler.utils.Config().prefix

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        guild_id = int(guild.id)
        await db.delete_guild(guild_id)
        self.bot.guild_data.pop(guild_id, None)


def setup(bot):
    bot.add_cog(Events(bot))
