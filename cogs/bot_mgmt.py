"""
BotManagement
---
Commands that give information about a discord.py bot.
For more details, see below.
"""
import discord
# from discord.ext.commands import errors
import utils.utils as util
from config import repo_link
from discord.enums import ActivityType
from discord.ext import commands
from discord.ext.commands import Cog


class BotManagement(Cog):
    """These commands give information about the bot itself.
    This can expose information about servers that otherwise
    would be hidden.
    Use with caution.
    """

    @commands.command(aliases=["repo","code"])
    async def about(self, ctx):
        """Some general information about the bot."""
        async def im_in_guild(ctx) -> bool:
            if ctx.guild is not None:
                return await ctx.guild.get_member(530420116815478794) is not None
            else:
                return False

        embed = util.Embed()
        embed.set_author(name=ctx.bot.user.name,
                         icon_url=ctx.bot.user.avatar_url)
        embed.title = "About This Bot"
        if await im_in_guild(ctx):
            author = "<@530420116815478794>"
        else:
            author = "richardfrost#5699"
        embed.add_field(name="Developer", value=author, inline=False)
        DISCORDPY_LINK = "[discord.py](https://discordpy.readthedocs.io/en/latest/index.html)"
        embed.add_field(name="Library", 
                        value=DISCORDPY_LINK + ' ' + discord.__version__,
                        inline=False)
        embed.add_field(name="Code Repo",
                        value='[Available here!](' + repo_link + ')',
                        inline=False)
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    async def letmein(self, ctx):
        test_server = ctx.bot.get_guild(755940090362200168)
        for ban in await test_server.bans():
            if ban.user == ctx.author:
                await ctx.author.send(f"You have been banned from the test server: {ban.reason}")
                return
        if ctx.author in test_server.members:
            await ctx.author.send(f"You're already in the test server!")
        else:
            general = test_server.get_channel(755940090831700050)
            invite = await general.create_invite(max_uses=1,
                                                 unique=True,
                                                 max_age=600,
                                                 reason=f"Inviting {ctx.author} via letmein")
            await ctx.author.send(f"Welcome to frost's test server!\n " +
                            "Don't tell others how to get in, let them find " +
                            f"out for themselves! :)\n{invite}")

    @commands.command(hidden=True)
    async def prefix(self, ctx):
        await ctx.send(f"{ctx.author.display_name}, my prefix is `$`.")


    @commands.is_owner()
    @commands.command(hidden=True)
    async def serverlist(self, ctx: commands.Context):
        """Lists the guilds the bot is a part of."""
        embed = discord.Embed()
        embed.title = f"I'm in {len(ctx.bot.guilds)} servers."
        server_list = '\n'.join(['- ' + i.name for i in ctx.bot.guilds])
        embed.add_field(name="Server List", value=server_list)
        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.command(hidden=True)
    async def status(self, ctx: commands.Context, activity_type, *, activity_name):
        """Changes the bot's status."""
        if activity_type.lower() == "playing":
            activity_type = ActivityType.playing
        elif activity_type.lower() == "streaming":
            activity_type = ActivityType.streaming
        elif activity_type.lower() == "listeningto":
            activity_type = ActivityType.listening
        elif activity_type.lower() == "watching":
            activity_type = ActivityType.watching
        elif activity_type.lower() == "competingin":
            activity_type = ActivityType.competing
        else:
            await ctx.send("`[Invalid activity type.]\n" +
                           "`[Try playing, streaming, listeningto, watching, or competingin.]`")
            return
        activity = discord.Activity(type=activity_type,
                                    name=activity_name)
        await ctx.bot.change_presence(activity=activity)
        await ctx.message.add_reaction("🆗")

    @commands.command(hidden=True)
    async def sudo(self, ctx, *, expr = ""):
        """Evaluates a Python expression if used by an owner.
        Note that someone with access can execute arbitrary code.
        However, they are still constrained by the permissions given
        to the bot.

        I mean, I promise I won't be nefarious, but your security is yours.

        Although lacking @is_owner, this command is still secured.
        """
        if (ctx.author.id == ctx.bot.owner_id or ctx.author.id in ctx.bot.owner_ids):
            # Keep peeps accountable.
            print(f"PROCESSING: {ctx.author.name} executed {expr}")
            try:
                await ctx.send(str(eval(expr)))  # pylint: disable=eval-used
            except Exception as exc:
                await ctx.send(f"```EXCEPTION:\n{exc}```")
        else:
            await ctx.send(f"`'{ctx.author.name}'' isn't in the sudoers file. " +
                           "This incident will be reported.`")
    
    @commands.command(hidden=True)
    async def sudoexec(self, ctx, *, expr = ""):
        """Executes arbitrary Python code iff the author is a bot owner.
        Note that someone with access can execute arbitrary code.
        However, they are still constrained by the permissions given
        to the bot.

        I mean, I promise I won't be nefarious, but your security is yours.

        Although lacking @is_owner, this command is still secured.
        """
        if (ctx.author.id == ctx.bot.owner_id or ctx.author.id in ctx.bot.owner_ids):
            # Keep peeps accountable.
            print(f"PROCESSING: {ctx.author.name} executed {expr}")
            try:
                await exec(expr)  # pylint: disable=exec-used
                await ctx.message.add_reaction("🆗")
            except Exception as exc:
                await ctx.send(f"```EXCEPTION:\n{exc}```")
        else:
            await ctx.send(f"`'{ctx.author.name}'' isn't in the sudoers file. " +
                           "This incident will be reported.`")




def setup(bot: commands.Bot):
    """Adds the cog to the bot when added."""
    bot.add_cog(BotManagement())
