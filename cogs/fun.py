
import re

import discord
import discord.ext.commands as commands
from discord.ext.commands import Cog

class Fun(Cog):

    @commands.command(brief="Show custom emoji",
                      help="Shows a bigger version of a custom emoji. Useful for stealing.",
                      usage="<custom emoji>")
    async def emoji(self, ctx, emoji):
        matchinfo = re.match(r'<(a?):(\w+):(\d+)>', emoji, flags=re.I)
        if matchinfo:
            matchinfogroups = matchinfo.groups()
            suffix = ".gif" if matchinfogroups[0] == 'a' else ".png"
            await ctx.send(f"https://cdn.discordapp.com/emojis/{matchinfogroups[2]}{suffix}")
        else:
            await ctx.send(f"{ctx.author.mention}, you need to select a valid " + 
                        "emoji.\n(Only custom emojis are accepted.)")
            
    @commands.command(brief="Repeat after me",
                      help="The bot will repeat whatever you say.")
    async def say(self, ctx, *, content):
        await ctx.send(content)
        if ctx.guild is not None:
            await ctx.message.delete()


def setup(bot: commands.Bot):
    bot.add_cog(Fun())
