import discord
from discord.ext import commands
import asyncio
import datetime

seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='mute')
    @commands.has_permissions(manage_roles=True)
    async def _mute(self, ctx: commands.Context, member: discord.Member, time: str = None):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.add_roles(role)
        await ctx.send(("Muted {}").format(member))
        if time:
            time = int(time[:-1]) * seconds_per_unit[time[-1]]
            await asyncio.sleep(time)
            await member.remove_roles(role)

    @commands.command(name='timeout')
    @commands.has_permissions(manage_roles=True)
    async def _timeout(self, ctx: commands.Context, member: discord.Member, duration: str = None):
        duration = int(duration[:-1]) * seconds_per_unit[duration[-1]]
        await member.timeout_for(duration=datetime.timedelta(seconds=duration))
        await ctx.send(("Timed out {}").format(member))


def setup(bot):
    bot.add_cog(Moderation(bot))
