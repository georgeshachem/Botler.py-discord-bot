import discord
from discord.ext import commands

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='avatar')
    async def _avatar(self, ctx: commands.Context, member: discord.Member = None):
        if not member:
            member = ctx.author
        em = discord.Embed(description=f"[Avatar URL]({member.display_avatar.url})")
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        em.set_image(url=member.display_avatar.url)
        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Misc(bot))