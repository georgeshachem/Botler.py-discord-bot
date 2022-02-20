from zoneinfo import ZoneInfo
from discord.ext import commands
from datetime import datetime
import aiohttp
from zoneinfo import ZoneInfo


LIRARATE_API_URL = "https://lirarate.org/wp-json/lirarate/v2/rates?currency=LBP&_ver={}"


class Lebanon(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='lbprate', aliases=['rate', 'usdrate', 'ratetoday'])
    async def _lbp_rate(self, ctx: commands.Context):
        current_dt = datetime.now()
        current_time = 't{dt.year}{dt.month}{dt.day}{dt.hour}'.format(
            dt=current_dt)
        current_url = LIRARATE_API_URL.format(current_time)
        async with aiohttp.ClientSession() as session:
            async with session.get(current_url) as response:
                data = await response.json()
        buy_data = data['buy'][-1]
        buy_timestamp, buy_price = buy_data[0], buy_data[1]
        sell_data = data['sell'][-1]
        sell_timestamp, sell_price = sell_data[0], sell_data[1]

        buy_timestamp = int(buy_timestamp)
        buy_timestamp /= 1000
        buy_dt = datetime.fromtimestamp(
            buy_timestamp).astimezone(ZoneInfo('Asia/Beirut'))
        time_text = buy_dt.strftime('%I:%M%p %d-%m-%Y')

        duration = current_dt - datetime.fromtimestamp(buy_timestamp)
        duration_in_s = duration.total_seconds()
        hours = int(duration_in_s//3600)
        minutes = int((duration_in_s % 3600)/60)

        await ctx.reply(f"Buy 1 USD at {buy_price} LBP\nSell 1 USD at {sell_price} LBP\nUpdated {hours} hours and {minutes} minutes ago at {time_text}")


def setup(bot):
    bot.add_cog(Lebanon(bot))
