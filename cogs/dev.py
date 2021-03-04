
import random


import aiohttp

import discord
from discord.errors import HTTPException
import discord.ext.commands as commands
from discord.ext.commands import Cog
from discord.ext.commands.errors import MissingRequiredArgument
import utils.utils as util
import utils.converters as converters


class Development(Cog):
    
    @commands.command(hidden=True)
    async def order(self, ctx):
        names = ['Aracelli', 'Chad', 'Mark', 'Nathan', 'Erik', 'Richard', 'Ryan']
        random.shuffle(names)
        embed = util.Embed()
        embed.description = "Scrum Order:\n" + "\n".join(names)
        await ctx.reply(embed=embed)

    @commands.command(hidden=True)
    async def hug(self, ctx: commands.Context, target: converters.I_MemberConverter):
        # Can't send a message to yourself. Acknowledge anyway.
        if target == ctx.bot.user:
            await ctx.message.add_reaction("💖")
            return
        # Get hug gif
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://purrbot.site/api/img/sfw/hug/gif") as response:
                resp_json = await response.json()
                if not resp_json["error"]:
                    hug_gif = resp_json["link"]
                else:
                    await ctx.send(f"`[Error in Purrbot's servers: '{resp_json['message']}'. Sorry!]`")
                    return
        # Construct embed to send
        embed = util.Embed()
        embed.title = "A hug for you!"
        embed.description = f"[Where from?]({ctx.message.jump_url})"
        embed.set_footer(text=f"Sent by {ctx.author.display_name}",
                         icon_url=ctx.author.avatar_url)
        embed.set_image(url=hug_gif)
        await target.send(embed=embed)
        await ctx.send(f"Hug on the way!", delete_after=5)

    @hug.error
    async def hug_error(self, ctx, error):
        if isinstance(error, commands.errors.MemberNotFound):
            await ctx.send(f"{ctx.author.mention}, I couldn't find them.")
        elif isinstance(error, discord.HTTPException) or isinstance(error, discord.errors.Forbidden):
            await ctx.send(f"{ctx.author.mention}, I couldn't send it to them. Maybe I'm blocked?")
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await self.hug(ctx, ctx.author)
        else:
            await ctx.send("something happened o_O")
        





def setup(bot):
    bot.add_cog(Development())