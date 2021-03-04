"""
Role Color Setter/Getter
by richardfrost

MIT License
"""

import discord
from discord.embeds import Embed
from discord.ext import commands

import utils.utils as util

roles_to_colors = {760690161033019423 : 776197851407319070,  # Staff
                   816150880730218576 : 816150975022104666,  # Developers
                   816151271693877258 : 816151442481217618,  # LDSG
                   816151794061148161 : 816151877074419743,  # Cute <3
                   816152516185423902 : 816152578186280960,  # Trusted
                  }

all_color_role_ids = [i[1] for i in roles_to_colors.items()]
# ^^ Gets the value for each item in the dictionary.

class Roles(commands.Cog):

    def cog_check(self, ctx):
        # """These commands only work in frost's test server."""
        if ctx.guild:
            return ctx.guild.id == 755940090362200168
        return False

    async def cog_command_error(self, ctx, error):
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
        color_roles = []
        member_rev_roles = member.roles
        member_rev_roles.reverse()
        # Get the user's role colors.
        for role in member_rev_roles:
            if role.id in roles_to_colors:
                color_role = guild.get_role(roles_to_colors[role.id])
                color_roles.append(color_role)
        # If there are roles, build and send the embed.
        if color_roles:
            embed = util.Embed()
            embed.set_author(name = member.display_name, 
                             icon_url = member.avatar_url)
            embed.title = "Equippable Color Inventory"
            embed.description = ("Equip a color role by using `!equip role" +
                                 " name` without the 'Colors'. \n" +
                                 "e.g. `!equip Trusted`\n\n")
            embed.description += '\n'.join([r.mention for r in color_roles])
            await ctx.send(embed=embed)
        # If not, tell the user.
        else:
            await ctx.send(f"{ctx.author.mention}, you don't have any colors" +
                           " in your inventory!")

    @commands.command(brief="Add a color",
                      help="Add a color from your inventory. It must be one" +
                           " that you have unlocked. Only available in" +
                           " the testing server.")
    async def equip(self, ctx, *, role_name):
        """Equips a color from your inventory."""
        member = ctx.author
        guild = ctx.guild
        role = discord.utils.find(lambda r: r.name.lower() == role_name.lower(), 
                                  guild.roles)
        if not bool(role):
            await ctx.send(f"{member.mention}, that is not a valid role.\n" +
                           "Try `!inventory` to see a list of available roles.",
                           delete_after=15)
        elif role not in member.roles:
            await ctx.send(f"{member.mention}, you don't have that role.\n" +
                           "Try `!inventory` to see a list of available roles.",
                           delete_after=15)
        elif role.id not in roles_to_colors:
            await ctx.send(f"{member.mention}, that role isn't equippable.\n" +
                           "Try `!inventory` to see a list of available roles.",
                           delete_after=15)
        else:
            # It exists, the member has it, and it's equippable.
            await member.remove_roles(*[discord.Object(i) for i in all_color_role_ids])
            added_color_role = guild.get_role(roles_to_colors[role.id])
            await member.add_roles(added_color_role)
            await ctx.message.add_reaction("👌")

    @commands.command(brief="Removes your color.",
                      help="Removes any colors you have equipped. Only " +
                           "available in the test server.")
    async def unequip(self, ctx):
        await ctx.author.remove_roles(*[discord.Object(i) for i in all_color_role_ids])
        await ctx.message.add_reaction("👌")



def setup(bot):
    bot.add_cog(Roles())
        

        
        
    

