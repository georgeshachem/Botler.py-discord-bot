import wavelink
from discord.ext import commands
from wavelink.ext import spotify


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEventPayload):
        if payload.player.queue.is_empty:
            await payload.player.disconnect()

    @commands.command(name='play', aliases=['p'])
    async def _play(self, ctx, *, search: str):
        """Play music from Spotify or YouTube
        """
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = ctx.voice_client

        # TODO: check for wavelink.exceptions.NoTracksError
        decoded = spotify.decode_url(search)
        tracks = []
        if decoded:
            # vc.autoplay = True
            match decoded['type']:
                case spotify.SpotifySearchType.track:
                    track = await spotify.SpotifyTrack.search(search, return_first=True)
                case spotify.SpotifySearchType.playlist:
                    tracks = []
                    async for partial in spotify.SpotifyTrack.iterator(query=search):
                        tracks.append(partial)
                    track = tracks[0]
                    if len(tracks) > 1:
                        tracks = tracks[1:]
                case _:
                    return await ctx.reply("Check Spotify URL, only song or playlists are supported")

        else:
            # vc.autoplay = False
            track = await wavelink.YouTubeTrack.search(search, return_first=True)

        if not vc.is_playing():
            await vc.play(track, populate=True)
        else:
            await vc.queue.put_wait(track)

        if tracks:
            for track in tracks:
                await vc.queue.put_wait(track)

    @commands.command(name='disconnect', aliases=['dc', 'stop'])
    async def _disconnect(self, ctx):
        """Simple disconnect command.
        This command assumes there is a currently connected Player.
        """
        vc: wavelink.Player = ctx.voice_client
        await vc.disconnect()

    @commands.command(name='queue')
    async def _queue(self, ctx: commands.Context):
        vc: wavelink.Player = ctx.voice_client

        if not vc:
            return await ctx.reply("Not connected...")

        await ctx.reply(vc.queue)

    @commands.command(name='next', aliases=['skip'])
    async def _next_song(self, ctx: commands.Context):
        vc: wavelink.Player = ctx.voice_client

        if not vc:
            return await ctx.reply("Not connected...")

        try:
            track = vc.queue.get()
            await vc.play(track)
        except wavelink.QueueEmpty:
            await ctx.reply("No song in queue")


async def setup(bot):
    await bot.add_cog(Music(bot))
