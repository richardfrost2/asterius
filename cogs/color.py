"""Color management for the URL Stans server."""

import discord
from discord.ext import commands

class ColorChange(commands.Cog):
    """Color management for URLStans"""

    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.command(aliases=["equip", "inventory", "inv"],
                      help="Allows you to change your color in URLStans. "
                           "Run with no arguments to see a list of colors, "
                           "or use !color <number> to equip a color.",
                      brief="Color management.",
                      usage="[number]")
    async def color(self, ctx, number = None):
        """With no arguments, shows the list of available colors.
        With a number, applies the role named "COLOR <number>"
        """
        # Get all color roles, in descending order
        roles = [r for r in ctx.guild.roles[::-1] if str(r).startswith("COLOR ")]
        if not number:
            # Prepare the embed.
            embed = discord.Embed(colour=discord.Color.random())
            embed.title = "Equipable Color Inventory"
            embed.description = ("Equip a color by using `!color <number>`.\n" +
                "For example, to equip `COLOR 0` use `!color 0`.\n\n" +
                "\n".join([role.mention for role in roles]))
            await ctx.send(embed=embed)
        else:
            if number.lower() == "clear":
                await ctx.author.remove_roles(roles,
                                              reason="Color change",
                                              atomic=True) # subject to change
                await ctx.message.add_reaction('👌')
            else:
                applied_role = discord.utils.get(roles, name="COLOR " + number)
                if applied_role:
                    await ctx.author.remove_roles(*roles,
                                                  reason="Color change",
                                                  atomic=True) # subject to change
                    await ctx.author.add_roles(applied_role,
                                                 reason="Color change")
                    await ctx.message.add_reaction('👌')
                else:
                    await ctx.send(ctx.author.mention + 
                                   ", I couldn't find the color you were looking for.")

def setup(bot):
    bot.add_cog(ColorChange())


            



