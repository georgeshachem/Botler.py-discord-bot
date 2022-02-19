import discord
from discord.ext import commands
import botler.database.models as models
import datetime


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='balance', aliases=['bal'])
    async def _balance(self, ctx: commands.Context, member: discord.Member = None):
        if not member:
            member = ctx.author
        member_balance = await models.Economy.query.where((models.Economy.guild_id == ctx.guild.id) & (models.Economy.member_id == member.id)).gino.first()
        if (not member_balance):
            member_balance = await models.Economy.create(guild_id=ctx.guild.id, member_id=member.id)
        embed = discord.Embed(
            title="Balance", timestamp=datetime.datetime.now())
        embed.set_author(name=f"{member.name}#{member.discriminator}",
                         icon_url=member.display_avatar.url)
        embed.add_field(
            name="Cash", value=member_balance.balance, inline=False)
        await ctx.reply(embed=embed)

    @commands.command(name='addmoney', aliases=['add-money'])
    @commands.has_permissions(manage_roles=True)
    async def _add_money(self, ctx: commands.Context, member: discord.Member, amount: int):
        member_balance = await models.Economy.query.where((models.Economy.guild_id == ctx.guild.id) & (models.Economy.member_id == member.id)).gino.first()
        if (member_balance):
            await member_balance.update(balance=member_balance.balance+amount).apply()
            new_balance = member_balance.balance
        else:
            await models.Economy.create(guild_id=ctx.guild.id, member_id=member.id, balance=amount)
            member_balance = amount
        await ctx.reply(
            f"Added {amount} to {member.name}#{member.discriminator}. His new balance is {new_balance}")

    @commands.command(name='editmoney', aliases=['edit-money', 'setmoney', 'set-money'])
    @commands.has_permissions(manage_roles=True)
    async def _edit_money(self, ctx: commands.Context, member: discord.Member, amount: int):
        member_balance = await models.Economy.query.where((models.Economy.guild_id == ctx.guild.id) & (models.Economy.member_id == member.id)).gino.first()
        if (member_balance):
            await member_balance.update(balance=amount).apply()
        else:
            await models.Economy.create(guild_id=ctx.guild.id, member_id=member.id, balance=amount)
        await ctx.reply(
            f"Set {member.name}#{member.discriminator} balance to {amount}")

    @commands.command(name='resetmoney', aliases=['reset-money'])
    @commands.has_permissions(manage_roles=True)
    async def _reset_money(self, ctx: commands.Context, member: discord.Member = None):
        if not member:
            member = ctx.author
        member_balance = await models.Economy.query.where((models.Economy.guild_id == ctx.guild.id) & (models.Economy.member_id == member.id)).gino.first()
        if (member_balance):
            await member_balance.update(balance=0).apply()
        else:
            await models.Economy.create(guild_id=ctx.guild.id, member_id=member.id)
        await ctx.reply(
            f"Resetted {member.name}#{member.discriminator} balance.")


def setup(bot):
    bot.add_cog(Economy(bot))
