import random

from discord.ext import commands


class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='choose', aliases=['select', 'pick'])
    async def _choose(self, ctx: commands.Context, *, options: str):
        options = options.split()
        await ctx.send(f"{ctx.author.mention} I pick {random.choice(options)}")

    @commands.command(name='roll')
    async def _roll(self, ctx: commands.Context, *, max_range: int = 6):
        await ctx.send(f"{ctx.author.mention} I rolled a {random.randint(1, max_range)}")

    @commands.command(name='coin', aliases=['flip', 'coinflip', 'cf'])
    async def _coin_flip(self, ctx: commands.Context):
        await ctx.send(f"{ctx.author.mention} I flipped a coin and got {random.choice(['head', 'tail'])}")


async def setup(bot):
    await bot.add_cog(Fun(bot))
