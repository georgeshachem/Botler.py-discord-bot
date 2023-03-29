import re

import discord
from asyncpg.exceptions import UniqueViolationError
from discord.ext import commands

import botler.database.models as models


class Custom(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='addcustom')
    @commands.has_permissions(manage_roles=True)
    async def _add_custom_role(self, ctx: commands.Context, role: discord.Role, icon_perm: bool = False):
        """
        *Mark a role as custom*
        **Example**: `{prefix}addcustom @customrole`
        """
        try:
            await models.CustomRole.create(guild_id=ctx.guild.id, role_id=role.id, icon_perm=icon_perm)
        except UniqueViolationError:
            return await ctx.send("Role is already added to the custom list")
        await ctx.send("Added custom role: {}".format(role))

    @commands.command(name='bulkaddcustom')
    @commands.has_permissions(manage_roles=True)
    async def _bulk_add_custom_role(self, ctx: commands.Context, icon_perm: bool, roles: commands.Greedy[discord.Role]):
        roles_already_added = []
        roles_error = []
        i = 0
        for role in roles:
            try:
                await models.CustomRole.create(guild_id=ctx.guild.id, role_id=role.id, icon_perm=icon_perm)
                i += 1
            except UniqueViolationError:
                roles_already_added.append(role.id)
            except Exception:
                roles_error.append(role.id)
        to_send = "Added custom roles: {}/{} ({} already added & {} errors)\n".format(
            i, len(roles), len(roles_already_added), len(roles_error))
        if len(roles_already_added) > 0:
            to_send += "Already added roles: "
            for role in roles_already_added:
                to_send += f"{ctx.guild.get_role(int(role))} | "
            to_send = to_send[:-3] + "\n"
        if len(roles_error) > 0:
            to_send += "Roles with error: "
            for role in roles_error:
                to_send += f"{ctx.guild.get_role(int(role))} | "
            to_send = to_send[:-3] + "\n"
        await ctx.send(to_send)

    @commands.command(name='enableicon')
    @commands.has_permissions(manage_roles=True)
    async def _enable_custom_icon(self, ctx: commands.Context, role: discord.Role, icon_perm: bool = True):
        custom_role = await models.CustomRole.query.where(
            (models.CustomRole.guild_id == ctx.guild.id) & (models.CustomRole.role_id == role.id)).gino.first()
        await custom_role.update(icon_perm=icon_perm).apply()
        await ctx.send("Updated custom role icon permission")

    @commands.command(name='bulkenableicon')
    @commands.has_permissions(manage_roles=True)
    async def _bulk_enable_custom_icon(self, ctx: commands.Context, icon_perm: bool,
                                       roles: commands.Greedy[discord.Role]):
        roles_error = []
        i = 0
        for role in roles:
            try:
                custom_role = await models.CustomRole.query.where(
                    (models.CustomRole.guild_id == ctx.guild.id) & (models.CustomRole.role_id == role.id)).gino.first()
                await custom_role.update(icon_perm=icon_perm).apply()
                i += 1
            except Exception:
                roles_error.append(role.id)

        to_send = "Updated custom roles icon perms: {}/{} ({} errors)\n".format(
            i, len(roles), len(roles_error))
        if len(roles_error) > 0:
            to_send += "Roles with error: "
            for role in roles_error:
                to_send += f"{ctx.guild.get_role(int(role))} | "
            to_send = to_send[:-3] + "\n"
        await ctx.send(to_send)

    @commands.command(name='deletecustom')
    @commands.has_permissions(manage_roles=True)
    async def _delete_custom_role(self, ctx: commands.Context, role: discord.Role):
        try:
            custom_role = await models.CustomRole.query.where(
                (models.CustomRole.guild_id == ctx.guild.id) & (models.CustomRole.role_id == role.id)).gino.first()
            await custom_role.delete()
        except Exception:
            return await ctx.send("Error deleting, try again")
        await ctx.send("Deleted custom role")

    @commands.command(name='viewcustoms')
    @commands.has_permissions(manage_roles=True)
    async def _view_custom_roles(self, ctx: commands.Context):
        custom_roles = await models.CustomRole.query.where(models.CustomRole.guild_id == ctx.guild.id).gino.all()
        if custom_roles:
            embed = discord.Embed(title="Custom Roles")
            for role in custom_roles:
                fetched_role = ctx.guild.get_role(int(role.role_id))
                if fetched_role:
                    if role.icon_perm:
                        embed.add_field(name=fetched_role.name,
                                        value=":white_check_mark:", inline=True)
                    else:
                        embed.add_field(name=fetched_role.name,
                                        value=":x:", inline=True)
                else:
                    await role.delete()
            if len(embed.fields) > 0:
                return await ctx.send(embed=embed)
            else:
                return await ctx.send("All of your set up custom roles got deleted")
        else:
            return await ctx.send("You don't have any custom role set up")

    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(name='changecolor')
    async def _change_color(self, ctx: commands.Context, color: str):
        match = re.search(r'^0x(?:[0-9a-fA-F]{3}){1,2}$', color)
        if match:
            custom_roles_raw = await models.CustomRole.query.where(
                models.CustomRole.guild_id == ctx.guild.id).gino.all()
            custom_roles_list = [x.role_id for x in custom_roles_raw]
            custom_role = next((
                x for x in ctx.author.roles if x.id in custom_roles_list), None)
            if custom_role:
                await custom_role.edit(colour=int(color, 16))
                await ctx.send("Color changed")
            else:
                await ctx.send("You don't have a custom role")
        else:
            await ctx.send("Invalid hex color. Example: 0xFF0000")

    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(name='changeicon')
    async def _change_icon(self, ctx: commands.Context):
        custom_roles_icon_raw = await models.CustomRole.query.where(
            (models.CustomRole.guild_id == ctx.guild.id) & (models.CustomRole.icon_perm == True)).gino.all()
        custom_roles_icon_list = [x.role_id for x in custom_roles_icon_raw]
        custom_role = next((
            x for x in ctx.author.roles if x.id in custom_roles_icon_list), None)
        if custom_role:
            try:
                new_icon = await ctx.message.attachments[0].read()
            except IndexError:
                return await ctx.send("Please provide an image as an attachment")
            await custom_role.edit(display_icon=new_icon)
            await ctx.send("Icon changed")
        else:
            await ctx.send("You don't have a custom icon")


async def setup(bot):
    await bot.add_cog(Custom(bot))
