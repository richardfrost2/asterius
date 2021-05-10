
import asyncio
import datetime
import config
import discord
from discord.ext import commands

class Embed(discord.Embed):
    """Embed with some prebuilt values."""
    def __init__(self):
        """Creates a new embed."""
        super().__init__()
        self.color = config.EMBED_COLOR
        self.timestamp = datetime.datetime.now()


async def confirm(ctx: commands.Context, *,
                  target_user = None,
                  channel = None,
                  prompt = "Are you sure?",
                  fields = {},
                  timeout = 15):
    """Confirm box for bot functions.

    **Parameters**
    ctx: Context
    target_user: The user to target with the embed. Default is ctx.author.
    channel: The channel for the embed to appear. Default is ctx.channel.
    prompt: The description of the embed. 
    fields: Additional fields for the embed. Optional.
      This should be a dict in {name: value} format.
    timeout: Time (in seconds) before the embed closes.
    """
    bot = ctx.bot
    buttons = ['✅', '⛔']
    embed = Embed()
    embed.color = discord.Color(0xff0000)
    if target_user:
        embed.set_author(name=target_user.display_name,
                         icon_url=target_user.avatar_url)
    else:
        embed.set_author(name=ctx.author.display_name,
                         icon_url=ctx.author.avatar_url)
    embed.title = f"Action Required - Answer in {timeout}s"
    embed.description = prompt
    for key in fields:
        embed.add_field(name=key, value=fields[key])
    embed.set_footer(text=f"{buttons[0]} to confirm, {buttons[1]} to deny.")
    if channel:
        try:
            dialog = await channel.send(embed=embed)
        except: # If it can't send to a DM, for instance.
            dialog = await ctx.send(embed=embed)
    else:
        dialog = await ctx.reply(embed=embed)
    for react in buttons:
        await dialog.add_reaction(react)

    def _is_valid_reaction(reaction, user) -> bool:
        """Helper check."""
        if target_user:
            return (str(reaction) in buttons and 
                    user == target_user and
                    reaction.message == dialog)
        else:
            return (str(reaction) in buttons and 
                    user == ctx.author and
                    reaction.message == dialog)
    
    try:
        response, _ = await bot.wait_for('reaction_add', timeout = timeout,
                                         check = _is_valid_reaction)
        await dialog.delete()
        if str(response) == buttons[0]:
            return True
        return False
    except asyncio.TimeoutError:
        await dialog.delete()
        return False
    

async def prefix(bot, msg):
    """Returns the prefix for the bot."""
    if msg.guild is None:
        prefix_val = '!'
    elif msg.guild.id in bot.prefixes:
        return commands.when_mentioned_or(bot.prefixes[msg.guild.id])(bot, msg)
    else:
        async with bot.db.acquire() as conn:
            prefix_val = await conn.fetchval(
                """SELECT prefix FROM guilds
                WHERE guild_id = $1""",
                msg.guild.id
            )
            bot.prefixes[msg.guild.id] = prefix_val
            if not prefix_val:
                return commands.when_mentioned(bot, msg)
    return commands.when_mentioned_or(prefix_val)(bot, msg)