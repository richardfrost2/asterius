"""
Main part of the bot.
"""

import re
import sys
import traceback

import discord
import discord.ext.commands as commands
from discord.ext.commands import errors
from discord.ext.commands.bot import when_mentioned_or

import config
import utils.help
import utils.utils as util

activity = discord.Activity(type=config.ACTIVITY_TYPE,
                            name=config.ACTIVITY_NAME)

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=when_mentioned_or('$'),
                   owner_id=config.OWNER,
                   activity=activity,
                   intents=intents,
                   help_command=utils.help.HelpCommand())

for extension in config.EXTENSIONS:
    bot.load_extension(extension)
print("Loading extensions complete!")

@bot.event
async def on_ready():
    """When the bot is ready. Don't do too much here."""
    print(f"Ready! Logged in as {bot.user}.")


@commands.is_owner()
@bot.command(hidden=True,
             name='exit')
async def _exit(ctx):
    """Causes the bot to close."""
    await ctx.message.add_reaction('🛏')  # bed
    await bot.close()

@commands.is_owner()
@bot.group(name='modules',
           invoke_without_command=True,
           brief="Manage loaded extensions.",
           help="Lets you manage extensions loaded.\n" +
                "Run without a subcommand to view loaded extensions.",
           hidden=True)
async def modules(ctx):
    """Shows a list of loaded extensions."""
    embed = discord.Embed()
    cogs_list = '\n'.join(['- ' + e for e in ctx.bot.extensions])
    if cogs_list != '':
        embed.add_field(name="Modules Loaded", value=cogs_list)
        await ctx.send(embed=embed)
        return
    await ctx.send("`[No modules loaded.]`")
    return

@commands.is_owner()
@modules.command(brief="Adds an extension.",
                 help="Loads an extension. Most of them are in the `cogs` " +
                      "folder.",
                 aliases=["load"],
                 usage="<extension name>")
async def add(ctx, extension):
    """Adds an extension"""
    try:
        bot.load_extension(extension)
        await ctx.message.add_reaction("🆗")
    except errors.ExtensionAlreadyLoaded:
        await ctx.send("`[Extension already loaded.]`")
    except errors.ExtensionNotFound:
        await ctx.send("`[Extension not found.]`")
    except errors.NoEntryPointError:
        await ctx.send("`[No entry point. Define 'setup' to continue.]`")
    except errors.ExtensionError:
        await ctx.send("`[Extension encountered an error setting up.]`")

@commands.is_owner()
@modules.command(brief="Removes an extension.",
                 help="Removes an extension from memory.",
                 aliases=["unload"],
                 usage="<extension name>")
async def remove(ctx, extension):
    """Removes an extension"""
    try:
        bot.unload_extension(extension)
        await ctx.message.add_reaction("🆗")
    except errors.ExtensionNotLoaded:
        await ctx.send("`[Extension not loaded.]`")

@commands.is_owner()
@modules.command(brief="Reloads an extension.",
                 help="Reloads an extension.",
                 aliases=["restart"],
                 usage="<extension name>")
async def reload(ctx, extension):
    """Reloads an extension"""
    try:
        bot.reload_extension(extension)
        await ctx.message.add_reaction("🆗")
    except errors.ExtensionNotLoaded:
        await ctx.send("`[Extension not loaded.]`")
    except errors.ExtensionNotFound:
        await ctx.send("`[Extension not found! It may have been removed.]`")
    except errors.NoEntryPointError:
        await ctx.send("`[No entry point. Define 'setup' to continue.]`")
    except errors.ExtensionError:
        await ctx.send("`[Extension encountered an error setting up.]`")

@bot.event
async def on_message(message):
    """Prints all received messages to console."""
    if message.guild is not None:
        print(f"[{message.guild.name[:8]}#{message.channel.name[:8]}] ", end = '')
    else:
        print(f"[DM {message.channel.recipient}] ", end = '')
    print(f"{message.author}: {message.clean_content}")
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, exc):
    """Handles errors in this bot."""
    ignored = (commands.CommandNotFound, commands.NotOwner)
    # If the command has an error handler, ignore it.
    if hasattr(ctx.command, 'on_error'):
        return
    # If the cog has an error handler, also ignore.
    if (ctx.cog is not None and
        ctx.cog._get_overridden_method(ctx.cog.cog_command_error) is not None):
        return
    # Catch common errors before printing tracebacks.
    if isinstance(exc, ignored):
        return
    if isinstance(exc, commands.DisabledCommand):
        await ctx.send("That command is currently disabled.",
                       delete_after=15)
        return
    if isinstance(exc, commands.NoPrivateMessage):
        await ctx.send("This command can only be used in servers.",
                       delete_after=15)
        return
    if isinstance(exc, (commands.BadArgument, commands.MissingRequiredArgument)):
        await ctx.send("I can't understand the input.\n"
                       f"Usage: `{ctx.prefix}{ctx.command.qualified_name} "
                       f"{ctx.command.usage}`",
                       delete_after=15)
    else:
        ### Send traceback to the errors channel via a webhook.
        # Get the webhook. (The channel only has one webhook)
        err_channel = bot.get_channel(config.ERROR_CHANNEL)
        webhook = (await err_channel.webhooks())[0]
        # Create webhook frame.
        error_embed = util.Embed()
        error_embed.title = type(exc).__name__
        error_embed.color = discord.Color.red()
        error_embed.description = "Message: " + str(exc)
        error_embed.set_author(name=bot.user.display_name,
                               icon_url=bot.user.avatar_url)
        # Get the traceback, and remove identifying file names.
        traceback_str = ''.join(traceback.format_tb(exc.__traceback__))
        paths_lower = [path.capitalize() for path in sys.path]
        all_paths_re = '(?:' + ")|(?:".join(paths_lower) + ')'
        all_paths_re = re.sub(r'\\', r'\\\\', all_paths_re)
        traceback_str = re.sub(all_paths_re, '', traceback_str)
        # Add the traceback to the embed.
        error_embed.add_field(name="Traceback", value=traceback_str)
        await webhook.send(embed=error_embed)

if __name__ == "__main__":
    bot.run(config.TOKEN)
