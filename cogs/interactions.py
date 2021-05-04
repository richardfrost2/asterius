"""a"""

import aiohttp
import discord
import discord.ext.commands as commands
import utils.converters as converters
import utils.utils as util
from discord.ext.commands import Cog


class Interactions(Cog):
    """Holds interactions between people."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Give some affection",
                      help="Give someone a hug! The recipient will receive a" +
                           " DM letting you know how much you care with a GIF.",
                      usage="[target]")
    async def hug(self, ctx: commands.Context, *, target: converters.I_MemberConverter):
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
                    await ctx.send("`[Error in Purrbot's servers: "
                                   f"'{resp_json['message']}'. Sorry!]`")
                    return
        # Construct embed to send
        embed = util.Embed()
        embed.title = "A hug for you!"
        embed.description = f"[Where from?]({ctx.message.jump_url})"
        embed.set_footer(text=f"Sent by {ctx.author.display_name}",
                         icon_url=ctx.author.avatar_url)
        embed.set_image(url=hug_gif)
        await target.send(embed=embed)
        await ctx.send("Hug on the way!", delete_after=10)

    @hug.error
    async def hug_error(self, ctx, error):
        if isinstance(error, commands.errors.MemberNotFound):
            await ctx.send(f"{ctx.author.mention}, I couldn't find them.")
        elif isinstance(error, (discord.HTTPException, discord.errors.Forbidden)):
            await ctx.send(f"{ctx.author.mention}, I couldn't send it to them. Maybe I'm blocked?")
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await self.hug(ctx, ctx.author)
        else:
            await ctx.send("something unusual happened o_O",
                           delete_after=10)
            raise error

def setup(bot):
    bot.add_cog(Interactions(bot))
