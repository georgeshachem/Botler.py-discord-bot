import discord
from discord.ext import commands
import botler.utils
import botler.database.models


class Management(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(manage_guild=True)
    @commands.command(name='prefix')
    async def _prefix(self, ctx: commands.Context, new_prefix: str = None):
        """
        *Change your servers prefix*
        **Example**: `{prefix}prefix !`
        """
        if not new_prefix:
            prefix = botler.utils.get_guild_prefix(self.bot, ctx.guild.id)
            embed = discord.Embed(description=f"Prefix currently set to `{prefix}`")
            await ctx.send(embed=embed)
            return
        embed = discord.Embed(description="Prefix changed")
        guild = await botler.database.models.Guild.get(ctx.guild.id)
        if guild is None:
            await botler.database.models.Guild.create(id=ctx.guild.id, prefix=new_prefix)
            self.bot.guild_data[ctx.guild.id] = {"prefix": new_prefix}
        else:
            embed.add_field(name="From", value=guild.prefix)
            await guild.update(prefix=new_prefix).apply()
            self.bot.guild_data[ctx.guild.id].update({"prefix": new_prefix})

        embed.add_field(name="To", value=new_prefix)
        await ctx.channel.send(embed=embed)



def setup(bot):
    bot.add_cog(Management(bot))