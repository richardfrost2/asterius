"""
Main part of the bot.
"""

import asyncio

from discord.ext.commands.bot import when_mentioned_or
import config
import discord
import discord.ext.commands as commands
from discord.ext.commands import errors


activity = discord.Activity(type=config.activity_type,
                            name=config.activity_name)

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=when_mentioned_or('$'),
                   owner_id=config.owner,
                   activity=activity,
                   intents=intents)

@bot.event
async def on_ready():
    """Loads all extensions.
    This may fire multiple times (i.e. after debugging) so don't do anything
    TOO crazy with it.
    """
    print(f"Ready! Logged in as {bot.user}.")
    for extension in config.extensions:
        bot.load_extension(extension)
    print("Default extensions loaded.")

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
           help="Lets you manage extensions loaded.",
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
@modules.command()
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
@modules.command()
async def remove(ctx, extension):
    """Removes an extension"""
    try:
        bot.unload_extension(extension)
        await ctx.message.add_reaction("🆗")
    except errors.ExtensionNotLoaded:
        await ctx.send("`[Extension not loaded.]`")

@commands.is_owner()
@modules.command()
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
    bot.run(config.token)
