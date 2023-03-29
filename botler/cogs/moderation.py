import discord
from discord.ext import commands
import asyncio
import datetime
import botler.database.models as models
import re


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
        if (member.top_role >= ctx.guild.me.top_role):
            return await ctx.send("I can't do that because this person has a higher role than me.")
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.remove_roles(role)
        await ctx.send(("Unmuted {}").format(member))

    @commands.command(name='timeout', aliases=['to'])
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

    @commands.command(name='untimeout', aliases=['uto'])
    @commands.has_permissions(manage_roles=True)
    async def _untimeout(self, ctx: commands.Context, member: discord.Member):
        if (member.top_role >= ctx.guild.me.top_role):
            return await ctx.send("I can't do that because this person has a higher role than me.")
        await member.remove_timeout()
        await ctx.send(("Removed {} from time out").format(member))

    @commands.command(name='warn')
    @commands.has_permissions(manage_roles=True)
    async def _warn(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        await models.Warn.create(guild_id=ctx.guild.id, user_id=member.id, reason=reason, moderator=f'{ctx.author.name}#{ctx.author.discriminator}')
        await ctx.send(("Warned {}").format(member))

    @commands.command(name='warns')
    @commands.has_permissions(manage_roles=True)
    async def _warns(self, ctx: commands.Context, member: discord.Member):
        member_warns = await models.Warn.query.where((models.Warn.user_id == member.id) & (models.Warn.guild_id == ctx.guild.id)).gino.all()
        embed = discord.Embed(
            title=f'Warnings for {member.name}#{member.discriminator} ({member.id}): {len(member_warns)}', color=0xff0000)
        for warn in member_warns:
            embed.add_field(name=f'ID: {warn.id} | By: {warn.moderator} | On: {warn.date.strftime("%d-%m-%Y")}',
                            value=f'{warn.reason}', inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
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
    @commands.has_permissions(ban_members=True)
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

    @commands.command(name='setnick')
    @commands.has_permissions(manage_roles=True)
    async def _set_nick(self, ctx: commands.Context, member: discord.Member, *, name: str = None):
        if (member.top_role >= ctx.author.top_role):
            return await ctx.send("You can't do that because this person has a higher role than you.")
        elif (member.top_role >= ctx.guild.me.top_role):
            return await ctx.send("I can't do that because this person has a higher role than me.")
        await member.edit(nick=name)
        await ctx.send(("Changed {} nickname").format(member))

    @commands.command(name='vmute')
    @commands.has_permissions(manage_roles=True)
    async def _voice_mute(self, ctx: commands.Context, member: discord.Member):
        if (member.top_role >= ctx.author.top_role):
            return await ctx.send("You can't do that because this person has a higher role than you.")
        elif (member.top_role >= ctx.guild.me.top_role):
            return await ctx.send("I can't do that because this person has a higher role than me.")
        await member.edit(mute=True)
        await ctx.send(("Muted {} in voice").format(member))

    @commands.command(name='vunmute')
    @commands.has_permissions(manage_roles=True)
    async def _voice_unmute(self, ctx: commands.Context, member: discord.Member):
        if (member.top_role >= ctx.guild.me.top_role):
            return await ctx.send("I can't do that because this person has a higher role than me.")
        await member.edit(mute=False)
        await ctx.send(("Unmuted {} in voice").format(member))

    @commands.command(name='deafen')
    @commands.has_permissions(manage_roles=True)
    async def _voice_deafen(self, ctx: commands.Context, member: discord.Member):
        if (member.top_role >= ctx.author.top_role):
            return await ctx.send("You can't do that because this person has a higher role than you.")
        elif (member.top_role >= ctx.guild.me.top_role):
            return await ctx.send("I can't do that because this person has a higher role than me.")
        await member.edit(deafen=True)
        await ctx.send(("Deafened {} in voice").format(member))

    @commands.command(name='undeafen')
    @commands.has_permissions(manage_roles=True)
    async def _voice_undeafen(self, ctx: commands.Context, member: discord.Member):
        if (member.top_role >= ctx.guild.me.top_role):
            return await ctx.send("I can't do that because this person has a higher role than me.")
        await member.edit(deafen=False)
        await ctx.send(("Undeafened {} in voice").format(member))

    @commands.has_permissions(manage_roles=True)
    @commands.guild_only()
    @commands.command(name='purge')
    async def _purge(self, ctx: commands.Context, amount: int = 99):
        await ctx.channel.purge(limit=amount+1)

    @commands.has_permissions(manage_roles=True)
    @commands.guild_only()
    @commands.command(name='role')
    async def _role(self, ctx: commands.Context, member: discord.Member, *, role: discord.Role):
        if role in member.roles:
            await member.remove_roles(role)
            await ctx.send(f"Removed role {str(role)} from {str(member)}")
        else:
            await member.add_roles(role)
            await ctx.send(f"Added role {str(role)} to {str(member)}")

    @commands.has_permissions(manage_roles=True)
    @commands.guild_only()
    @commands.command(name='roleadd', aliases=['addrole', 'arole', 'rolea'])
    async def _role_add(self, ctx: commands.Context, member: discord.Member, *, role: discord.Role):
        if role in member.roles:
            await ctx.send(f"{str(member)} already has role {str(role)}")
        else:
            await member.add_roles(role)
            await ctx.send(f"Added role {str(role)} to {str(member)}")

    @commands.has_permissions(manage_roles=True)
    @commands.guild_only()
    @commands.command(name='roleremove', aliases=['removerole', 'rrole', 'roler'])
    async def _role_remove(self, ctx: commands.Context, member: discord.Member, *, role: discord.Role):
        if role in member.roles:
            await member.remove_roles(role)
            await ctx.send(f"Removed role {str(role)} from {str(member)}")
        else:
            await ctx.send(f"{str(member)} does not have the role {str(role)}")

    @commands.has_permissions(manage_roles=True)
    @commands.guild_only()
    @commands.command(name='rolecolor')
    async def _role_color(self, ctx: commands.Context, role: discord.Role, color: str):
        match = re.search(r'^0x(?:[0-9a-fA-F]{3}){1,2}$', color)
        if match:
            await role.edit(colour=int(color, 16))
            await ctx.reply(f"Edit color of role {str(role)}")
        else:
            await ctx.reply("Invalid hex color. Example: 0xFF0000")


async def setup(bot):
    await bot.add_cog(Moderation(bot))
