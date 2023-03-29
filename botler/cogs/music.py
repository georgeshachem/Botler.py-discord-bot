import wavelink
from discord.ext import commands


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='play', aliases=['p'])
    async def _play(self, ctx, *, search: str):
        """Simple play command."""

        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = ctx.voice_client

        track = await wavelink.YouTubeTrack.search(search, return_first=True)
        await vc.play(track)

    @commands.command(name='disconnect', aliases=['dc', 'stop'])
    async def _disconnect(self, ctx):
        """Simple disconnect command.
        This command assumes there is a currently connected Player.
        """
        vc: wavelink.Player = ctx.voice_client
        await vc.disconnect()


async def setup(bot):
    await bot.add_cog(Music(bot))
