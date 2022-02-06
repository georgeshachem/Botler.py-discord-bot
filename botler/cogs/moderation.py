import discord
from discord.ext import commands
import asyncio
import datetime
import botler.database.models as models

seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='mute')
    @commands.has_permissions(manage_roles=True)
    async def _mute(self, ctx: commands.Context, member: discord.Member, time: str = None):
        if (ctx.author == member):
            return await ctx.send("You can't mute yourself.")
        elif (ctx.guild.me == member):
            return await ctx.send("You can't mute me.")
        elif (member.top_role >= ctx.author.top_role):
            return await ctx.send("You can't do that because this person has a higher role than you.")
        elif (member.top_role >= ctx.guild.me.top_role):
            return await ctx.send("I can't do that because this person has a higher role than me.")
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.add_roles(role)
        await ctx.send(("Muted {}").format(member))
        if time:
            time = int(time[:-1]) * seconds_per_unit[time[-1]]
            await asyncio.sleep(time)
            await member.remove_roles(role)

    @commands.command(name='unmute')
    @commands.has_permissions(manage_roles=True)
    async def _unmute(self, ctx: commands.Context, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.remove_roles(role)
        await ctx.send(("Unmuted {}").format(member))

    @commands.command(name='timeout')
    @commands.has_permissions(manage_roles=True)
    async def _timeout(self, ctx: commands.Context, member: discord.Member, duration: str = None):
        if (ctx.author == member):
            return await ctx.send("You can't time out yourself.")
        elif (ctx.guild.me == member):
            return await ctx.send("You can't time out me.")
        elif (member.top_role >= ctx.author.top_role):
            return await ctx.send("You can't do that because this person has a higher role than you.")
        elif (member.top_role >= ctx.guild.me.top_role):
            return await ctx.send("I can't do that because this person has a higher role than me.")
        duration = int(duration[:-1]) * seconds_per_unit[duration[-1]]
        await member.timeout_for(duration=datetime.timedelta(seconds=duration))
        await ctx.send(("Timed out {}").format(member))

    @commands.command(name='warn')
    @commands.has_permissions(manage_roles=True)
    async def _warn(self, ctx: commands.Context, member: discord.Member, reason: str = None):
        await models.Warn.create(guild_id=ctx.guild.id, user_id=member.id, reason=reason, moderator=f'{ctx.author.name}#{ctx.author.discriminator}')
        await ctx.send(("Warned {}").format(member))

    @commands.command(name='warns')
    @commands.has_permissions(manage_roles=True)
    async def _warns(self, ctx: commands.Context, member: discord.Member):
        member_warns = await models.Warn.query.where(models.Warn.user_id == member.id).gino.all()
        embed = discord.Embed(
            title=f'Warnings for {member.name}#{member.discriminator} ({member.id}): {len(member_warns)}', color=0xff0000)
        for warn in member_warns:
            embed.add_field(name=f'ID: {warn.id} | By: {warn.moderator} | On: {warn.date.strftime("%d-%m-%Y")}',
                            value=f'{warn.reason}', inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='kick')
    @commands.has_permissions(manage_roles=True)
    async def _kick(self, ctx: commands.Context, member: discord.Member, reason: str = None):
        if (ctx.author == member):
            return await ctx.send("You can't kick yourself.")
        elif (ctx.guild.me == member):
            return await ctx.send("You can't kick me.")
        elif (member.top_role >= ctx.author.top_role):
            return await ctx.send("You can't do that because this person has a higher role than you.")
        elif (member.top_role >= ctx.guild.me.top_role):
            return await ctx.send("I can't do that because this person has a higher role than me.")
        await member.kick(reason=reason)
        await ctx.send(("Kicked {}").format(member))

    @commands.command(name='ban')
    @commands.has_permissions(manage_roles=True)
    async def _ban(self, ctx: commands.Context, member: discord.Member, reason: str = None):
        if (ctx.author == member):
            return await ctx.send("You can't ban yourself.")
        elif (ctx.guild.me == member):
            return await ctx.send("You can't ban me.")
        elif (member.top_role >= ctx.author.top_role):
            return await ctx.send("You can't do that because this person has a higher role than you.")
        elif (member.top_role >= ctx.guild.me.top_role):
            return await ctx.send("I can't do that because this person has a higher role than me.")
        await member.ban(reason=reason)
        await ctx.send(("Banned {}").format(member))


def setup(bot):
    bot.add_cog(Moderation(bot))
