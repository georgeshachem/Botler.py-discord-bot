import discord
from discord.ext import commands
from zoneinfo import ZoneInfo
from datetime import datetime
import aiohttp
from zoneinfo import ZoneInfo
import matplotlib.pyplot as plt
import numpy as np
import io
import re


LIRARATE_API_URL = "https://lirarate.org/wp-json/lirarate/v2/rates?currency=LBP&_ver={}"


class Lebanon(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.lirarate_data = None
        self.cached = None
        self.last_fecthed = None
        self.caching_time_minutes = 5

    @commands.Cog.listener()
    async def on_message(self, message):
        if (message.author.bot):
            return
        if message.channel.id == 982583730348646410:
            if (len(message.attachments) > 0):
                submission = message.attachments[0]
                async with aiohttp.ClientSession() as session:
                    async with session.get(submission.url) as response:
                        if (response.status == 200):
                            submission_image = io.BytesIO(await response.read())
                        else:
                            return await message.send(f"{message.author.mention} couldn't download your submission, please try again")
                submission_channel = message.guild.get_channel(
                    982660446492454912)
                await submission_channel.send(f"Submission by {message.author.mention}", file=discord.File(submission_image, filename=f"{message.author.id}.jpg"))
                await message.channel.send(f"{message.author.mention} your submission has been sent to another hidden channel so only mods can see it!")
            else:
                await message.channel.send(f"{message.author.mention} are you sure you sent an image?")
            await message.delete()

    async def update_lirarate_data(self):
        current_dt = datetime.now()
        if (self.lirarate_data):
            time_diff = (current_dt -
                         self.last_fecthed).total_seconds() / 60.0
        else:
            time_diff = self.caching_time_minutes + 1
        if (time_diff > self.caching_time_minutes):
            current_time = 't{dt.year}{dt.month}{dt.day}{dt.hour}'.format(
                dt=current_dt)
            current_url = LIRARATE_API_URL.format(current_time)
            async with aiohttp.ClientSession() as session:
                async with session.get(current_url) as response:
                    if (response.status == 200):
                        data = await response.json()
                        self.lirarate_data = data
                        self.cached = False
                        self.last_fecthed = current_dt
                    else:
                        self.cached = True
        else:
            self.cached = True

    @commands.command(name='lbprate', aliases=['rate', 'usdrate', 'ratetoday'])
    async def _lbp_rate(self, ctx: commands.Context):
        await self.update_lirarate_data()

        buy_data = self.lirarate_data['buy'][-1]
        buy_timestamp, buy_price = buy_data[0], buy_data[1]
        sell_data = self.lirarate_data['sell'][-1]
        sell_price = sell_data[1]

        buy_timestamp = int(buy_timestamp)
        buy_timestamp /= 1000
        buy_dt = datetime.fromtimestamp(
            buy_timestamp).astimezone(ZoneInfo('Asia/Beirut'))
        time_text = buy_dt.strftime('%I:%M %p %d/%m/%Y')

        duration = datetime.now() - \
            datetime.fromtimestamp(buy_timestamp)
        duration_in_s = duration.total_seconds()
        hours = int(duration_in_s//3600)
        minutes = int((duration_in_s % 3600)/60)

        await ctx.reply(f"Buy 1 USD at {buy_price:,} LBP\nSell 1 USD at {sell_price:,} LBP\nUpdated {hours} hours and {minutes} minutes ago at {time_text}\nCached: {self.cached}")

    @commands.command(name='convert', aliases=['usdtolbp'])
    async def _convert_usd_to_lbp(self, ctx: commands.Context, amount: int):
        await self.update_lirarate_data()

        buy_data = self.lirarate_data['buy'][-1]
        buy_price = buy_data[1]

        converted_amount = amount * int(buy_price)

        await ctx.reply(f"{amount:,} USD = {converted_amount:,.2f} LBP")

    @commands.command(name='lbpconvert', aliases=['lbptousd'])
    async def _convert_lbp_to_usd(self, ctx: commands.Context, amount: int):
        await self.update_lirarate_data()

        sell_data = self.lirarate_data['sell'][-1]
        sell_price = sell_data[1]

        converted_amount = amount / int(sell_price)

        await ctx.reply(f"{amount:,} LBP = {converted_amount:,.2f} USD")

    @commands.command(name='lbpgraph')
    async def _lbp_graph(self, ctx: commands.Context):
        await self.update_lirarate_data()

        buy_data = self.lirarate_data['buy'][-100:]

        x = np.array([datetime.fromtimestamp(elt[0]/1000) for elt in buy_data])
        y = np.array([elt[1] for elt in buy_data])

        plt.plot(x, y)
        plt.xticks(rotation=45)
        plt.subplots_adjust(bottom=0.2)
        graph_file = io.BytesIO()
        plt.savefig(graph_file, format='png')
        graph_file.seek(0)
        plt.cla()

        await ctx.reply(file=discord.File(graph_file, filename="lbpgraph.png"))


def setup(bot):
    bot.add_cog(Lebanon(bot))
