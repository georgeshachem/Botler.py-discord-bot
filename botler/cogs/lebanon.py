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
GUILD_ID = 719643607195451552
ROLE_ID = 895429738540171337


class Lebanon(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.lirarate_data = None
        self.cached = None
        self.last_fecthed = None
        self.caching_time_minutes = 5
        self.to_oppress = []

    @commands.Cog.listener()
    async def on_member_update(self, member_before, member_after):
        if member_before.guild.id == GUILD_ID and member_before.id in self.to_oppress:
            role = discord.utils.get(member_before.guild.roles, id=ROLE_ID)
            if role not in member_after.roles:
                await member_after.add_roles(role)

    @commands.has_permissions(manage_guild=True)
    @commands.command(name='oppress')
    async def _oppress(self, ctx: commands.Context, member: discord.Member):
        self.to_oppress.append(member.id)
        role = discord.utils.get(member.guild.roles, id=ROLE_ID)
        await member.add_roles(role)
        await ctx.reply(f"Oppressing {member.name}")

    @commands.has_permissions(manage_guild=True)
    @commands.command(name='unoppress')
    async def _unoppress(self, ctx: commands.Context, member: discord.Member):
        if member.id in self.to_oppress:
            self.to_oppress.remove(member.id)
            role = discord.utils.get(member.guild.roles, id=ROLE_ID)
            if role in member.roles:
                await member.remove_roles(role)
            await ctx.reply(f"Unppressing {member.name}")
        else:
            await ctx.reply(f"{member.name} is not oppressed")

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
