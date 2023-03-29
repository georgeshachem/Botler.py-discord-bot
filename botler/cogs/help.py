import discord
from discord.ext import commands
from discord.errors import Forbidden


async def send_embed(ctx, embed):
    try:
        await ctx.send(embed=embed)
    except Forbidden:
        try:
            await ctx.send("Hey, seems like I can't send embeds. Please check my permissions :)")
        except Forbidden:
            await ctx.author.send(
                f"Hey, seems like I can't send any message in {ctx.channel.name} on {ctx.guild.name}\n"
                f"May you inform the server team about this issue? :slight_smile: ", embed=embed)


class Help(commands.Cog):
    """
    Sends this help message
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    # @commands.bot_has_permissions(add_reactions=True,embed_links=True)
    async def help(self, ctx: commands.Context, input: str = None):
        """Help command"""

        if (input is None):
            embed = discord.Embed(title='Categories and commands', color=discord.Color.blue(),
                                  description=f'Use `{ctx.prefix}help <category|command>` to gain more information about a category or command')
            for cog_name in self.bot.cogs:
                cog_commands_text = ''
                cog = self.bot.get_cog(cog_name)
                cog_commands = cog.get_commands()
                if (cog_commands):
                    for command in cog_commands:
                        if (not command.hidden):
                            cog_commands_text += f' • `{command.name}`'
                    if (cog_commands_text):
                        embed.add_field(
                            name=cog_name, value=cog_commands_text[3:], inline=False)
        else:
            cog = self.bot.get_cog(input.title())
            if (cog is not None):
                embed = discord.Embed(title=cog.qualified_name, color=discord.Color.gold(),
                                      description=f'Use `{ctx.prefix}help <command>` to gain more information about a specific command')
                cog_commands = cog.get_commands()
                cog_commands_text = ''
                for command in cog_commands:
                    if (not command.hidden):
                        cog_commands_text += f'**{command.name}** - {command.short_doc}\n'
                if (cog_commands_text):
                    embed.add_field(name='Commands',
                                    value=cog_commands_text, inline=False)
                else:
                    embed = discord.Embed(title="Category or command not found", color=discord.Color.red(),
                                          description=f'This category or command can not be found! Please check again.')
            else:
                command = self.bot.get_command(input)
                if (command is not None and not command.hidden):
                    embed = discord.Embed(title=command.name, color=discord.Color.green(),
                                          description=f'{(command.help).format(prefix=ctx.prefix)}')
                else:
                    embed = discord.Embed(title="Category or command not found", color=discord.Color.red(),
                                          description=f'This category or command can not be found! Please check again.')

        await send_embed(ctx, embed)


async def setup(bot):
    await bot.add_cog(Help(bot))
