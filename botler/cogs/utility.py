import sys
import time
from datetime import datetime
import discord
from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.now().replace(microsecond=0)


    @commands.command()
    async def ping(self, ctx):
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

    @commands.command()
    async def uptime(self, ctx):
        """*Current uptime of the bot*
        **Example**: `{prefix}uptime`"""
        current_time = datetime.now().replace(microsecond=0)
        embed = discord.Embed(
            description=f"Time since I went online: {current_time - self.start_time}."
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def info(self, ctx):
        """*Shows stats and infos about the bot*
        **Example**: `{prefix}info`"""
        embed = discord.Embed(title="Botler")
        # embed.url = f"https://top.gg/bot/{self.bot.user.id}"
        embed.set_thumbnail(url=self.bot.user.avatar_url)
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
            f"discord.py: {discord.__version__}\n"
            f"Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}```",
            inline=False,
        )
        embed.add_field(
            name="Links",
            value=f"[Invite]({self.bot.invite})",
            inline=False,
        )
        embed.set_footer(text="Thank you for using Botler <3", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["socials", "links", "support"])
    async def invite(self, ctx):
        """*Shows invite link and other socials for the bot*
        **Aliases**: `socials`, `links`, `support`
        **Example**: `{prefix}invite`"""
        embed = discord.Embed()
        embed.description = f"[Invite]({self.bot.invite})"
        embed.set_footer(text="Thank you for using Botler <3", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))
