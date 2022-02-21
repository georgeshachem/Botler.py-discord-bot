from discord.ext import commands
import aiohttp
import os
import matplotlib.pyplot as plt
import numpy as np
import io
import discord
from datetime import datetime

COINGECKO_SEARCH_API_URL = "https://api.coingecko.com/api/v3/search?query={}"
COINGECKO_PRICE_API_URL = "https://api.coingecko.com/api/v3/simple/price?ids={}&vs_currencies=usd"
COINGECKO_PRICE_HISTORY_API_URL = "https://api.coingecko.com/api/v3/coins/{}/market_chart?vs_currency=usd&days={}"

ALPHA_ADVANTAGE_API_KEY = os.getenv("ALPHA_ADVANTAGE_API_KEY")
ALPHA_ADVANTAGE_API_URL = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={}&apikey={}"


class Trading(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.lirarate_data = None
        self.current_lirarate_dt = None

    async def get_crypto_match(self, param: str):
        current_url = COINGECKO_SEARCH_API_URL.format(param)
        async with aiohttp.ClientSession() as session:
            async with session.get(current_url) as response:
                if (response.status == 200):
                    data = await response.json()
                    coins = data['coins']
                    if (coins):
                        return coins[0]
                    else:
                        return None
                else:
                    return None

    async def get_crypto_price(self, coin: dict):
        coin_id = coin['id']
        current_url = COINGECKO_PRICE_API_URL.format(coin_id)
        async with aiohttp.ClientSession() as session:
            async with session.get(current_url) as response:
                if (response.status == 200):
                    data = await response.json()
                    return data[coin_id]['usd']
                else:
                    return None

    async def get_crypto_history(self, coin: dict, days: str):
        coin_id = coin['id']
        current_url = COINGECKO_PRICE_HISTORY_API_URL.format(coin_id, days)
        async with aiohttp.ClientSession() as session:
            async with session.get(current_url) as response:
                if (response.status == 200):
                    data = await response.json()
                    return data['prices']
                else:
                    return None

    async def get_stock_price(self, symbol: str):
        current_url = ALPHA_ADVANTAGE_API_URL.format(
            symbol, ALPHA_ADVANTAGE_API_KEY)
        async with aiohttp.ClientSession() as session:
            async with session.get(current_url) as response:
                if (response.status == 200):
                    data = await response.json()
                    stocks = data['Global Quote']
                    if (stocks):
                        return stocks['01. symbol'], stocks['05. price']
                    else:
                        return None
                else:
                    return None

    @commands.command(name='crypto', aliases=['c'])
    async def _crypto_price(self, ctx: commands.Context, *, coin: str):
        coin_match = await self.get_crypto_match(coin)
        if (coin_match):
            coin_price = await self.get_crypto_price(coin_match)
            if (coin_price):
                await ctx.reply(f"{coin_match['name']} = {coin_price} USD")
            else:
                await ctx.reply("An error occured when fetching the price.")
        else:
            await ctx.reply("Can't find this coin.")

    @commands.command(name='cryptochart', aliases=['cchart'])
    async def _crypto_chart(self, ctx: commands.Context, days: int, *, coin: str):
        coin_match = await self.get_crypto_match(coin)
        if (coin_match):
            coin_price_history = await self.get_crypto_history(coin_match, days)
            if (coin_price_history):
                x = np.array([datetime.fromtimestamp(elt[0]/1000)
                             for elt in coin_price_history])
                y = np.array([elt[1] for elt in coin_price_history])

                plt.plot(x, y)
                plt.xticks(rotation=45)
                plt.subplots_adjust(bottom=0.2)
                graph_file = io.BytesIO()
                plt.savefig(graph_file, format='png')
                graph_file.seek(0)
                plt.cla()

                await ctx.reply(file=discord.File(graph_file, filename="crypto_history.png"))
            else:
                await ctx.reply("An error occured when fetching the price.")
        else:
            await ctx.reply("Can't find this coin.")

    @commands.command(name='stock', aliases=['s'])
    async def _stock_price(self, ctx: commands.Context, *, symbol: str):
        stock_symbol, stock_price = await self.get_stock_price(symbol)
        if (stock_symbol and stock_price):
            await ctx.reply(f"{stock_symbol} = {stock_price} USD")
        else:
            await ctx.reply("Can't find this stock/symbol.")


def setup(bot):
    bot.add_cog(Trading(bot))
