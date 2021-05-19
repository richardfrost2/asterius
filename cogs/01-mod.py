"""Moderation commands."""

import discord
from discord.ext import commands
from utils import converters, utils as util

class Moderation(commands.Cog):
    """Commands for moderation."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="For great justice.",
                      help="Bans someone from your server.",
                      usage="<member>")
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.has_guild_permissions(ban_members=True)
    async def ban(self, ctx, member: converters.I_MemberConverter, *, reason):
        if member == ctx.author:
            await ctx.send(f"{ctx.author.mention}, you can't ban yourself.")
            return
        if member.top_role >= ctx.author.top_role:
            await ctx.send(f"{ctx.author.mention}, you cannot ban {member.mention},"
                           f" you don't have permission! (they have the high role)")
            return
        if member == ctx.me:
            await ctx.send("Nah. (Use Server Settings > Integrations to remove me)")
            return
        if await util.confirm(ctx,
                              prompt=f"Are you sure you want to ban {member}?"
                                     "(This will delete one day of their messages.)",
                              fields={"Created":member.created_at, "Joined":member.joined_at},
                              timeout=30):
            try:
                await member.send(f"You have been banned from {ctx.guild} by"
                                  f"{ctx.author.display_name}\n"
                                  f"Reason: {reason}")
            except:
                pass
            await ctx.guild.ban(member, str(ctx.author) + reason)
            await ctx.message.add_reaction('🔨')
        else:
            await ctx.message.add_reaction('❌')

    @commands.Cog.listener(name="on_message")
    async def begone(self, message):
        """Allows shouting BEGONE at people in your server for a more flashy
        ban command.
        """
        if message.content.lower().startswith('begone'):
            perms = message.author.permissions_in(message.channel)
            if perms.ban_members:
                if message.reference and message.reference.resolved:
                    ctx = await self.bot.get_context(message)
                    await self.ban(ctx, message.reference.resolved.author,
                                   reason = message.clean_content)


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