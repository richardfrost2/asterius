"""
Role Color Setter/Getter
by richardfrost

MIT License
"""

import discord
from discord.ext import commands

import utils.utils as util

ROLES_TO_COLORS = {760690161033019423 : 776197851407319070,  # Staff
                   816150880730218576 : 816150975022104666,  # Developers
                   816151271693877258 : 816151442481217618,  # LDSG
                   816151794061148161 : 816151877074419743,  # Cute <3
                   816152516185423902 : 816152578186280960,  # Trusted
                  }

ALL_COLOR_ROLES = [i[1] for i in ROLES_TO_COLORS.items()]
# ^^ Gets the value for each item in the dictionary.

class Roles(commands.Cog):

    def cog_check(self, ctx):
        # """These commands only work in frost's test server."""
        if ctx.guild:
            return ctx.guild.id == 755940090362200168
        raise NotInGuild()

    async def cog_command_error(self, ctx, error):
        if isinstance(error, NotInGuild):
            await ctx.send("This command can only be used in the testing "
                           "server.",
                           delete_after=15)
        if isinstance(error, commands.errors.CheckFailure):
            return
        else:
            print(error)


    @commands.command(aliases=["inv"],
                      brief="List available colors.",
                      help="Lists all the colors you have. Only works in the" +
                           " test server.")
    async def inventory(self, ctx):
        """Sends an embed with the available color list."""
        member = ctx.author
        guild = ctx.guild
        pref = ctx.prefix
        color_roles = []
        member_rev_roles = member.roles
        member_rev_roles.reverse()
        # Get the user's role colors.
        for role in member_rev_roles:
            if role.id in ROLES_TO_COLORS:
                color_role = guild.get_role(ROLES_TO_COLORS[role.id])
                color_roles.append(color_role)
        # If there are roles, build and send the embed.
        if color_roles:
            embed = util.Embed()
            embed.set_author(name = member.display_name, 
                             icon_url = member.avatar_url)
            embed.title = "Equippable Color Inventory"
            embed.description = (f"Equip a color role by using `{pref}equip role" +
                                 " name` without the 'Colors'. \n" +
                                 f"e.g. `{pref}equip Trusted`\n\n")
            embed.description += '\n'.join([r.mention for r in color_roles])
            await ctx.send(embed=embed)
        # If not, tell the user.
        else:
            await ctx.send(f"{ctx.author.mention}, you don't have any colors" +
                           " in your inventory!")

    @commands.command(brief="Add a color",
                      help="Add a color from your inventory. It must be one" +
                           " that you have unlocked. Only available in" +
                           " the testing server.",
                      usage="<role name>")
    async def equip(self, ctx, *, role_name):
        """Equips a color from your inventory."""
        member = ctx.author
        guild = ctx.guild
        pref = ctx.prefix
        role = discord.utils.find(lambda r: r.name.lower() == role_name.lower(), 
                                  guild.roles)
        if not bool(role):
            await ctx.send(f"{member.mention}, that is not a valid role.\n" +
                           f"Try `{pref}inventory` to see a list of available roles.",
                           delete_after=15)
        elif role not in member.roles:
            await ctx.send(f"{member.mention}, you don't have that role.\n" +
                           f"Try `{pref}inventory` to see a list of available roles.",
                           delete_after=15)
        elif role.id not in ROLES_TO_COLORS:
            await ctx.send(f"{member.mention}, that role isn't equippable.\n" +
                           f"Try `{pref}inventory` to see a list of available roles.",
                           delete_after=15)
        else:
            # It exists, the member has it, and it's equippable.
            await member.remove_roles(*[discord.Object(i) for i in ALL_COLOR_ROLES])
            added_color_role = guild.get_role(ROLES_TO_COLORS[role.id])
            await member.add_roles(added_color_role)
            await ctx.message.add_reaction("👌")

    @commands.command(brief="Removes your color.",
                      help="Removes any colors you have equipped. Only " +
                           "available in the test server.")
    async def unequip(self, ctx):
        await ctx.author.remove_roles(*[discord.Object(i) for i in ALL_COLOR_ROLES])
        await ctx.message.add_reaction("👌")

class NotInGuild(commands.CheckFailure):
    """Raised when the context is not in the testing server."""
    pass

def setup(bot):
    bot.add_cog(Roles())
        

        
        
    

