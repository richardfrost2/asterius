"""Moderation commands."""

import discord
from discord.ext import commands
from utils import converters, utils as util

class Moderation(commands.Cog):
    """Commands for moderation."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage="[member]")
    async def info(self, ctx, *, member: converters.I_MemberConverter = None):
        """Get information on a member."""
        if member is None:
            member = ctx.author
        embed = util.Embed()
        if member.nick:
            embed.set_author(name = f"{member.display_name} ({member})",
                             icon_url = member.avatar_url)
        else:
            embed.set_author(name = str(member), icon_url = member.avatar_url)
        embed.description = "(" + member.mention + ")"
        TIME_FORMAT = r"%a, %d %b %Y %X UTC"
        # Example: "Sun, 28 Mar 2021 18:54:22 UTC"
        embed.add_field(name="ID", value = member.id)
        embed.add_field(name="Joined",
                        value=member.joined_at.strftime(TIME_FORMAT))
        # ^ member.joined_at can be None but this is so uncommon I'm ignoring.
        embed.add_field(name="Account Created",
                        value=member.created_at.strftime(TIME_FORMAT))
        if member.bot:
            embed.add_field(name="Bot Invite Link",
                            value="[Invite Bot](" # more below
        f"{discord.utils.oauth_url(member.id, scopes=('bot', 'applications.commands'))})")
        await ctx.send(embed=embed)
        

def setup(bot):
    bot.add_cog(Moderation(bot))