
import random
import re

import discord
import discord.ext.commands as commands
from discord.ext.commands import Cog
import utils.utils as util

class Fun(Cog):


    @commands.command(brief="Chooses from a selection.",
                      help="Helps you make a choice between multiple options.",
                      usage="<option 1> | <option 2> | <option 3> ...",
                      aliases=["pick","choice","decide","random"])
    async def choose(self, ctx, *, choices):
        choices_list = choices.split('|')
        if len(choices_list) > 1:
            choice = random.choice(choices_list)
            await ctx.send(f"{ctx.author.mention}, my choice is **{choice}**.")
        else:
            await ctx.send(f"{ctx.author.mention}, you need to give me " +
                    "multiple options! `a | b ...`",
                     delete_after=20)





    @commands.command(brief="Show custom emoji",
                      help="Shows a bigger version of a custom emoji. Useful for stealing.",
                      usage="<custom emoji>",
                      hidden=True)
    async def emoji_old(self, ctx, emoji):
        matchinfo = re.match(r'<(a?):(\w+):(\d+)>', emoji, flags=re.I)
        if matchinfo:
            matchinfogroups = matchinfo.groups()
            suffix = ".gif" if matchinfogroups[0] == 'a' else ".png"
            await ctx.send(f"https://cdn.discordapp.com/emojis/{matchinfogroups[2]}{suffix}")
        else:
            await ctx.send(f"{ctx.author.mention}, you need to select a valid " + 
                        "emoji.\n(Only custom emojis are accepted.)")

    @commands.command(brief="Show emoji information",
                      help="Shows information about an emoji, as well as a"
                           "larger image.",
                      usage="<custom emoji>")
    async def emoji(self, ctx, emoji: discord.PartialEmoji):
        embed = util.Embed()
        embed.set_image(emoji.url)
        embed.title = emoji.name
        if emoji.id:
            embed.set_footer(text=f"ID: {emoji.id} - created")
            embed.timestamp = emoji.created_at
        else:
            embed.set_footer(text="Default Emoji")
            
    @commands.is_owner()
    @commands.command(brief="Repeat after me",
                      help="The bot will repeat whatever you say.")
    async def say(self, ctx, *, content):
        await ctx.send(content)
        if ctx.guild is not None:
            await ctx.message.delete()


def setup(bot: commands.Bot):
    bot.add_cog(Fun())
