"""
Main part of the bot.
"""

import asyncio

from discord.ext.commands.bot import when_mentioned_or
import config
import discord
import discord.ext.commands as commands
from discord.ext.commands import errors
import utils.help


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
    """Loads all extensions.
    This may fire multiple times (i.e. after debugging) so don't do anything
    TOO crazy with it.
    """
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
        print("[DM] ", end = '')
    print(f"{message.author}: {message.clean_content}")
    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(config.TOKEN)
