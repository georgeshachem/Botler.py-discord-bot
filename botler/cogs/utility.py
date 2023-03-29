import sys
import time
from datetime import datetime

import discord
from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.now().replace(microsecond=0)

    @commands.command(name='ping')
    async def _ping(self, ctx: commands.Context):
        """*Current ping and latency of the bot*
        **Example**: {}ping""".format(ctx.prefix)
        embed = discord.Embed()
        embed.add_field(name="Pinging...", value=f"wait")
        before_time = time.time()
        msg = await ctx.send(embed=embed)
        embed.clear_fields()
        latency = round(self.bot.latency * 1000)
        elapsed_ms = round((time.time() - before_time) * 1000) - latency
        embed.add_field(name="ping", value=f"{elapsed_ms}ms")
        embed.add_field(name="latency", value=f"{latency}ms")
        await msg.edit(embed=embed)

    @commands.command(name='uptime')
    async def _uptime(self, ctx: commands.Context):
        """*Current uptime of the bot*
        **Example**: `{prefix}uptime`"""
        current_time = datetime.now().replace(microsecond=0)
        embed = discord.Embed(
            description=f"Time since I went online: {current_time - self.start_time}."
        )
        await ctx.send(embed=embed)

    @commands.command(name='avatar')
    async def _avatar(self, ctx: commands.Context, member: discord.Member = None):
        if not member:
            member = ctx.author
        em = discord.Embed(
            description=f"[Avatar URL]({member.display_avatar.url})")
        em.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        em.set_image(url=member.display_avatar.url)
        await ctx.send(embed=em)

    @commands.has_permissions(manage_roles=True)
    @commands.guild_only()
    @commands.command(name='whois', aliases=['info', 'userinfo'])
    async def _user_info(self, ctx: commands.Context, member: discord.Member = None):
        if not member:
            member = ctx.message.author
        roles = [role for role in (member.roles)[1:]]
        embed = discord.Embed(colour=discord.Colour.blue(), timestamp=ctx.message.created_at,
                              title=f"User Info - {member}")
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="User ID:", value=member.id)
        embed.add_field(name="Display Name:", value=member.display_name)
        embed.add_field(name="Account Created On:", value=member.created_at.strftime(
            "%a, %#d %B %Y, %I:%M %p UTC"))
        embed.add_field(name="Joined Server On:", value=member.joined_at.strftime(
            "%a, %#d %B %Y, %I:%M %p UTC"))
        embed.add_field(name="Roles:", value=" ".join(
            [role.mention for role in roles]) if roles else None)
        embed.add_field(name="Highest Role:", value=member.top_role.mention)
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name='botinfo', aliases=['binfo'])
    async def _bot_info(self, ctx: commands.Context):
        """*Shows stats and infos about the bot*
        **Example**: `{prefix}info`"""
        embed = discord.Embed(title="Botler")
        # embed.url = f"https://top.gg/bot/{self.bot.user.id}"
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_field(
            name="Bot Stats",
            value=f"```py\n"
                  f"Guilds: {len(self.bot.guilds)}\n"
                  f"Users: {len(self.bot.users)}\n"
                  f"Shards: {self.bot.shard_count}\n"
                  f"Shard ID: {ctx.guild.shard_id}```",
            inline=False,
        )
        embed.add_field(
            name=f"Server Configuration",
            value=f"```\n"
                  f"Prefix: {ctx.prefix}\n"
                  f"```",
            inline=False,
        )
        embed.add_field(
            name="Software Versions",
            value=f"```py\n"
                  f"py-cord: {discord.__version__}\n"
                  f"Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}```",
            inline=False,
        )
        embed.add_field(
            name="Links",
            value=f"[Invite]({self.bot.invite})",
            inline=False,
        )
        embed.set_footer(text="Thank you for using Botler <3",
                         icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name='invite', aliases=["socials", "links", "support"])
    async def _invite(self, ctx):
        """*Shows invite link and other socials for the bot*
        **Aliases**: `socials`, `links`, `support`
        **Example**: `{prefix}invite`"""
        embed = discord.Embed()
        embed.description = f"[Invite]({self.bot.invite})"
        embed.set_footer(text="Thank you for using Botler <3",
                         icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Utility(bot))
