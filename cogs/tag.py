"""
Tag command for servers that do that.
"""

import discord
import discord.ext.commands as commands

class Tags(commands.Cog):
    """Holds tags."""

    @commands.group()
    async def tag(self, ctx, *, tagname = None):
        if tagname == None:
            await ctx.send_help(ctx.command)
        else:
            pass # Get tag and display it
    