import discord
from discord.ext import commands
import botler.database.models as models


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='balance', aliases=['bal'])
    @commands.has_permissions(manage_roles=True)
    async def _balance(self, ctx: commands.Context, member: discord.Member = None):
        if not member:
            member = ctx.author
        member_balance = await models.Economy.query.where((models.Economy.guild_id == ctx.guild.id) & (models.Economy.member_id == member.id)).gino.first()
        await ctx.reply(f"Your current balance is {member_balance.balance}")


def setup(bot):
    bot.add_cog(Economy(bot))
