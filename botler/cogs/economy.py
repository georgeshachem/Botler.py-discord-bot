import datetime

import discord
from discord.ext import commands

import botler.database.models as models


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='balance', aliases=['bal'])
    async def _balance(self, ctx: commands.Context, member: discord.Member = None):
        if not member:
            member = ctx.author
        member_balance = await models.Economy.query.where(
            (models.Economy.guild_id == ctx.guild.id) & (models.Economy.member_id == member.id)).gino.first()
        if not member_balance:
            member_balance = await models.Economy.create(guild_id=ctx.guild.id, member_id=member.id)
        embed = discord.Embed(
            title="Balance", timestamp=datetime.datetime.now())
        embed.set_author(name=f"{member.name}#{member.discriminator}",
                         icon_url=member.display_avatar.url)
        embed.add_field(
            name="Cash", value=member_balance.balance, inline=False)
        await ctx.reply(embed=embed)

    @commands.command(name='addmoney', aliases=['add-money'])
    @commands.check_any(commands.has_permissions(manage_roles=True), commands.is_owner())
    async def _add_money(self, ctx: commands.Context, member: discord.Member, amount: int):
        member_balance = await models.Economy.query.where(
            (models.Economy.guild_id == ctx.guild.id) & (models.Economy.member_id == member.id)).gino.first()
        if member_balance:
            await member_balance.update(balance=member_balance.balance + amount).apply()
            new_balance = member_balance.balance
        else:
            await models.Economy.create(guild_id=ctx.guild.id, member_id=member.id, balance=amount)
            new_balance = amount
        await ctx.reply(
            f"Added {amount} to {member.mention}. His new balance is {new_balance}")

    @commands.command(name='editmoney', aliases=['edit-money', 'setmoney', 'set-money'])
    @commands.check_any(commands.has_permissions(manage_roles=True), commands.is_owner())
    async def _edit_money(self, ctx: commands.Context, member: discord.Member, amount: int):
        member_balance = await models.Economy.query.where(
            (models.Economy.guild_id == ctx.guild.id) & (models.Economy.member_id == member.id)).gino.first()
        if member_balance:
            await member_balance.update(balance=amount).apply()
        else:
            await models.Economy.create(guild_id=ctx.guild.id, member_id=member.id, balance=amount)
        await ctx.reply(
            f"Set {member.mention} balance to {amount}")

    @commands.command(name='resetmoney', aliases=['reset-money'])
    @commands.check_any(commands.has_permissions(manage_roles=True), commands.is_owner())
    async def _reset_money(self, ctx: commands.Context, member: discord.Member = None):
        if not member:
            member = ctx.author
        member_balance = await models.Economy.query.where(
            (models.Economy.guild_id == ctx.guild.id) & (models.Economy.member_id == member.id)).gino.first()
        if member_balance:
            await member_balance.update(balance=0).apply()
        else:
            await models.Economy.create(guild_id=ctx.guild.id, member_id=member.id)
        await ctx.reply(
            f"Resetted {member.mention} balance.")

    @commands.command(name='additem', aliases=['add-item', 'createitem', 'create-item'])
    @commands.has_permissions(manage_roles=True)
    async def _add_item(self, ctx: commands.Context, name: str, price: int = 0, description: str = None,
                        stock: int = -1, role_required: discord.Role = None,
                        role_given: discord.Role = None, role_removed: discord.Role = None, required_balance: int = 0,
                        reply: str = None):
        price = abs(price)
        required_balance = abs(required_balance)
        role_required = role_required.id if role_required else None
        role_given = role_given.id if role_given else None
        role_removed = role_removed.id if role_removed else None
        await models.Item.create(guild_id=ctx.guild.id, name=name, price=price, description=description, stock=stock,
                                 role_required=role_required, role_given=role_given, role_removed=role_removed,
                                 required_balance=required_balance, reply=reply)
        await ctx.reply("Item added")

    @commands.command(name='buyitem', aliases=['buy-item', 'buy'])
    @commands.has_permissions(manage_roles=True)
    async def _buy_item(self, ctx: commands.Context, name: str):
        item = await models.Item.query.where(
            (models.Item.guild_id == ctx.guild.id) & (models.Item.name == name)).gino.first()
        if item:
            if item.price > 0:
                member_balance = await models.Economy.query.where((models.Economy.guild_id == ctx.guild.id) & (
                            models.Economy.member_id == ctx.author.id)).gino.first()
                new_balance = member_balance.balance - item.price
                if new_balance > 0:
                    await member_balance.update(balance=new_balance).apply()
                else:
                    return await ctx.reply("You don't have enough money.")

            if item.stock > 0:
                await item.update(stock=item.stock - 1).apply()
            elif item.stock == 0:
                return await ctx.reply("This item is out of stock.")

            if item.role_required:
                fetched_role = ctx.guild.get_role(item.role_required)
                if fetched_role:
                    if fetched_role not in ctx.author.roles:
                        return await ctx.reply("You don't have the required role to buy this item.")
                else:
                    return await ctx.reply("This item's required role does not exist. Contact an admin.")

            if item.role_given:
                fetched_role = ctx.guild.get_role(item.role_given)
                if fetched_role:
                    await ctx.author.add_roles(fetched_role)
                else:
                    return await ctx.reply("This item's role to add does not exist. Contact an admin.")

            if item.role_removed:
                fetched_role = ctx.guild.get_role(item.role_removed)
                if fetched_role:
                    if fetched_role in ctx.author.roles:
                        await ctx.author.remove_roles(fetched_role)
                else:
                    return await ctx.reply("This item's role to remove does not exist. Contact an admin.")

            if item.required_balance:
                member_balance = await models.Economy.query.where((models.Economy.guild_id == ctx.guild.id) & (
                            models.Economy.member_id == ctx.author.id)).gino.first()
                if member_balance.balance < item.required_balance:
                    return await ctx.reply("You need a higher balance.")

            if item.reply:
                await ctx.reply(item.reply)

            await ctx.reply("Item bought!")

        else:
            return await ctx.reply("Item not found! Check the name spelling.")

    @commands.command(name='edititem', aliases=['edit-item'])
    @commands.has_permissions(manage_roles=True)
    async def _edit_item(self, ctx: commands.Context, option: str, name: str, new_vlaue):
        item = await models.Item.query.where(
            (models.Item.guild_id == ctx.guild.id) & (models.Item.name == name)).gino.first()
        if item:
            role_converter = commands.RoleConverter()

            if option == "name":
                await item.update(name=str(new_vlaue)).apply()
                return await ctx.reply("Updated name")
            elif option == "price":
                await item.update(price=abs(int(new_vlaue))).apply()
                return await ctx.reply("Updated price")
            elif option == "description":
                await item.update(description=str(new_vlaue)).apply()
                return await ctx.reply("Updated description")
            elif option == "stock":
                await item.update(stock=int(new_vlaue)).apply()
                return await ctx.reply("Updated stock")
            elif option == "role_required":
                role = await role_converter.convert(ctx, new_vlaue)
                await item.update(role_required=role.id).apply()
                return await ctx.reply("Updated role required")
            elif option == "role_given":
                role = await role_converter.convert(ctx, new_vlaue)
                await item.update(role_given=role.id).apply()
                return await ctx.reply("Updated role given")
            elif option == "role_removed":
                role = await role_converter.convert(ctx, new_vlaue)
                await item.update(role_removed=role.id).apply()
                return await ctx.reply("Updated role removed")
            elif option == "required_balance":
                await item.update(required_balance=abs(int(new_vlaue))).apply()
                return await ctx.reply("Updated required balance")
            elif option == "reply":
                await item.update(reply=str(new_vlaue)).apply()
                return await ctx.reply("Updated reply")
            else:
                return await ctx.reply("Invalid option!")
        else:
            return await ctx.reply("Item not found! Check the name spelling.")

    @commands.command(name='removeitem', aliases=['remove-item', 'deleteitem', 'delete-item'])
    @commands.has_permissions(manage_roles=True)
    async def _remove_item(self, ctx: commands.Context, name: str):
        item = await models.Item.query.where(
            (models.Item.guild_id == ctx.guild.id) & (models.Item.name == name)).gino.first()
        if item:
            await item.delete()
            await ctx.reply("Item deleted")
        else:
            return await ctx.reply("Item not found! Check the name spelling.")

    @commands.command(name='store', aliases=['shop'])
    async def _store(self, ctx: commands.Context):
        items = await models.Item.query.where(models.Item.guild_id == ctx.guild.id).gino.all()
        if items:
            embed = discord.Embed(title="Shop")
            for item in items:
                embed.add_field(name=f"{item.name}",
                                value=f"${item.price}", inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.reply("Shop is empty...")


async def setup(bot):
    await bot.add_cog(Economy(bot))
