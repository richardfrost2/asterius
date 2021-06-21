"""
Role Color Setter/Getter
by frost

Now you're thinking with databases!
"""

import discord
from discord.ext import commands
from discord.mentions import AllowedMentions
import utils.utils as util


class Roles(commands.Cog):
    def __init__(self, bot):
        """This is required for DB connectivity."""
        self.bot = bot

    @commands.command(aliases=["inv"],
                      brief="List available colors.",
                      help="Lists all the colors you have. Only works in the" +
                           " test server.")
    async def inventory(self, ctx):
        """Sends an embed with the available color list."""
        member = ctx.author
        guild = ctx.guild
        pref = ctx.prefix
        guild_roles = await self._get_guild_roles(ctx.guild)

        color_roles = [] # Holds color roles
        member_rev_roles = member.roles
        member_rev_roles.reverse() # I think d.py has them low to high.
        # Get the user's role colors.
        for role in member_rev_roles:
            if role.id in guild_roles:
                # for color_role_id in guild_roles[role.id]:
                #     color_role = guild.get_role(color_role_id)
                #     color_roles.append(color_role)
                color_role = guild.get_role(guild_roles[role.id])
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
    async def equip(self, ctx, *, role_name: str):
        """Equips a color from your inventory."""
        member = ctx.author
        guild = ctx.guild
        pref = ctx.prefix
        # These two lines could be done smoother to reduce DB calls.
        # But no one really uses my bot so I should be fine.
        guild_roles = await self._get_guild_roles(guild)
        guild_color_roles = await self._get_guild_color_roles(guild)
        role_name = role_name.lower().replace(" colors", "")
        role = discord.utils.find(lambda r: r.name.lower() == role_name, 
                                  guild.roles)
        if not bool(role):
            await ctx.send(f"{member.mention}, that is not a valid role.\n" +
                           f"Try `{pref}inventory` to see a list of available roles.",
                           delete_after=15)
        elif role not in member.roles:
            await ctx.send(f"{member.mention}, you don't have that role.\n" +
                           f"Try `{pref}inventory` to see a list of available roles.",
                           delete_after=15)
        elif role.id not in guild_roles:
            await ctx.send(f"{member.mention}, that role isn't equippable.\n" +
                           f"Try `{pref}inventory` to see a list of available roles.",
                           delete_after=15)
        else:
            # It exists, the member has it, and it's equippable.
            await member.remove_roles(*[discord.Object(i) for i in guild_color_roles])
            added_color_role = guild.get_role(guild_roles[role.id])
            await member.add_roles(added_color_role)
            await ctx.message.add_reaction("👌")

    @commands.command(brief="Removes your color.",
                      help="Removes any colors you have equipped. Only " +
                           "available in the test server.")
    async def unequip(self, ctx):
        color_roles = await self._get_guild_color_roles(ctx.guild)
        await ctx.author.remove_roles(*[discord.Object(i) for i in color_roles])
        await ctx.message.add_reaction("👌")


    @commands.has_permissions(manage_roles=True)
    @commands.has_guild_permissions(manage_roles=True)
    @commands.command(brief="Imports a role and color",
                      help="Use this to add a color role into the database. "
                      "Use a 'key' role, and that name + ' Colors' needs to be valid.",
                      usage="<key role name/mention>")
    async def importcolor(self, ctx, role: discord.Role):
        color_role = discord.utils.find(lambda r: r.name == role.name + " Colors", 
                                        ctx.guild.roles)
        if not color_role:
            await ctx.send("Sorry, I couldn't find a matching color role!",
                           delete_after=15)
            return
        # Now that we verified both roles exist, add it to the DB.
        await self._add_role(ctx.guild, role.id, color_role.id)
        await ctx.send(f"Success! {role.mention} connected to {color_role.mention}",
                       allowed_mentions = discord.AllowedMentions.none(),
                       delete_after = 15)

    @commands.has_permissions(manage_roles=True)
    @commands.has_guild_permissions(manage_roles=True)
    @commands.command(brief="Creates a role and color",
                      help="Create a pair of roles connected in the database.",
                      usage="<role name>")
    async def createcolor(self, ctx, *, role_name):
        guild = ctx.guild
        key = await guild.create_role(name = role_name,
                                      reason = f"Color role requested by {ctx.author} - key")
        color = await guild.create_role(name = role_name + " Colors",
                                        reason = f"Color role requested by {ctx.author} - color")
        await self._add_role(ctx.guild, key.id, color.id)
        await ctx.send(f"Roles {key.mention} and {color.mention} created!\n"
                       "Next steps:\n- Put roles in order\n"
                       "- Apply a color to the color role\n"
                       "- Apply key role to people",
                       delete_after = 20)

    @commands.has_permissions(manage_roles=True)
    @commands.has_guild_permissions(manage_roles=True)
    @commands.command(brief="Deletes a color",
                      help="Use this to disconnect a color from the database. "
                      "Use a 'key' role.",
                      usage="<key role name/mention>")
    async def deletecolor(self, ctx, role: discord.Role):
        await self._delete_role(role.id)
        await ctx.send(f"All connections to {role.mention} removed.",
                       allowed_mentions = discord.AllowedMentions.none(),
                       delete_after = 15)
    

    async def _get_guild_roles(self, guild):
        """Gets records from one guild.
        Like ROLES_TO_COLORS was in the last iteration.
        """
        async with self.bot.db.acquire() as conn:
            roles = await conn.fetch(
                """SELECT * FROM colorroles WHERE guild_id = $1""",
                guild.id
            )
        # Roles is a list of Records containing
        # [role_id (internal), guild_id, key_role, color_role]
        output = {}
        for role in roles:
            # if role["key_role"] not in output:
            #    output[role["key_role"]] = []
            output[role["key_role"]] = role["color_role"]
        # output is now {key role : color role}, kinda like ROLES_TO_COLORS 
        # was in the old version.
        # Currently only 1:1 is supported but it could be changed in !equip.
        # If so the commented lines above should help.
        return output

    async def _get_guild_color_roles(self, guild):
        """Gets all color roles (no keys) from a guild.
        Like ALL_COLOR_ROLES in the last iteration.
        Returns a list of IDs.
        """
        async with self.bot.db.acquire() as conn:
            roles = await conn.fetch(
                """SELECT color_role FROM colorroles WHERE guild_id = $1""",
                guild.id
            )
        return [role['color_role'] for role in roles]

    async def _add_role(self, guild, key_role_id, color_role_id):
        """Adds a role to the DB."""
        async with self.bot.db.acquire() as conn:
            await conn.execute(
                """INSERT INTO colorroles (guild_id, key_role, color_role)
                VALUES ($1, $2, $3)
                """,
                guild.id, key_role_id, color_role_id
            )

    async def _delete_role(self, key_role_id):
        """Removes a color role from the DB."""
        async with self.bot.db.acquire() as conn:
            await conn.execute(
                """DELETE FROM colorroles WHERE key_role = $1""",
                key_role_id
            )
    
def setup(bot):
    bot.add_cog(Roles(bot))
