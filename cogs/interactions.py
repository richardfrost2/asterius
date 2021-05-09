"""Interact with people in fun ways with this cog!

Currently only used to send hugging gifs but it may grow!
"""

import aiohttp
import discord
import discord.ext.commands as commands
import utils.converters as converters
import utils.utils as util
from discord.ext.commands import Cog


class Interactions(Cog):
    """Holds interactions between people."""

    def __init__(self, bot):
        """Sets the bot for DB purposes"""
        self.bot = bot
        self.cache = {}

    @commands.command(brief="Give some affection",
                      help="Give someone a hug! The recipient will receive a" +
                           " DM letting you know how much you care with a GIF.",
                      usage="[target]")
    async def hug(self, ctx: commands.Context, *, target: converters.I_MemberConverter):
        # Can't send a message to yourself. Acknowledge anyway.
        if target == ctx.bot.user:
            await ctx.message.add_reaction("💖")
            return
        if not await self._get_status(target):
            await ctx.send("That person doesn't want to be hugged.",
                           delete_after=15)
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
        elif isinstance(error, (discord.HTTPException, discord.Forbidden)):
            await ctx.send(f"{ctx.author.mention}, I couldn't send it to them. Maybe I'm blocked?")
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await self.hug(ctx, target=ctx.author)
        else:
            await ctx.send("something unusual happened o_O",
                           delete_after=10)

    @commands.command(brief = "Change your interactions setting",
                      help = "Change whether you want to receive interactions,"
                             " such as hugs. Turn it on or off, or leave it"
                             " blank to see your current status.",
                      usage = "[on|off]")
    async def interactions(self, ctx, toggle_state: bool = None):
        """Lets you know your interactions state, or changes it."""
        status = await self._get_status(ctx.author)
        status_txt = "can" if status else "cannot"
        if toggle_state is None:
            await ctx.send(f"{ctx.author.mention}, you currently "
                           f"**{status_txt}** receive interactions.")
        else:
            await self._change_status(ctx.author, toggle_state)
            status_txt = "will" if toggle_state else "will not"
            await ctx.send(f"Success! {ctx.author.mention}, you now"
                           f" **{status_txt}** receive interactions.")

    # DB Commands below
    async def _get_status(self, user):
        """Gets the interaction status of the user."""
        # Check the cache first.
        if user.id in self.cache:
            return self.cache[user.id]
        async with self.bot.db.acquire() as conn:
            status = await conn.fetchval("SELECT huggable FROM users "
                                         "WHERE user_id = $1",
                                         user.id)
            self.cache[user.id] = status
            return status

    async def _change_status(self, user, status):
        async with self.bot.db.acquire() as conn:
            await conn.execute("UPDATE users SET huggable = $1 "
                               "WHERE user_id = $2",
                               status,
                               user.id)
        self.cache[user.id] = status

def setup(bot):
    bot.add_cog(Interactions(bot))
