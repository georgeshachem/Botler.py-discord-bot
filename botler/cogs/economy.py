import discord
from discord.ext import commands
import botler.database.models as models
import datetime


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='balance', aliases=['bal'])
    @commands.has_permissions(manage_roles=True)
    async def _balance(self, ctx: commands.Context, member: discord.Member = None):
        if not member:
            member = ctx.author
        member_balance = await models.Economy.query.where((models.Economy.guild_id == ctx.guild.id) & (models.Economy.member_id == member.id)).gino.first()
        embed = discord.Embed(
            title="Balance", timestamp=datetime.datetime.now())
        embed.set_author(name=f"{member.name}#{member.discriminator}",
                         icon_url=member.display_avatar.url)
        embed.add_field(
            name="Cash", value=member_balance.balance, inline=False)
        await ctx.reply(embed=embed)


def setup(bot):
    bot.add_cog(Economy(bot))
