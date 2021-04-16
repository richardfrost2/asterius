"""Listener cog for database functions"""

import discord
import discord.ext.commands as commands

class DBHelp(commands.Cog):
    """Holds listeners to keep the bot up to date."""

    def __init__(self, bot):
        """Classic bot setup function."""
        self.bot = bot

    @commands.is_owner()
    @commands.command(hidden=True,
                      brief="Refresh DB values",
                      help="Attempts to add all missing users and guilds to the DB.",
                      usage="")
    async def refreshdb(self, ctx):
        """Manually updates the db."""
        for guild in self.bot.guilds:
            await self.on_guild_join(self, guild)
        for user in self.bot.users:
            await self.on_member_join(self, user)
        await ctx.message.add_reaction('🆗')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if await self._get_user(self, member.id):
            pass
        else:
            await self._add_user(self, member.id)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if await self._get_guild(guild.id):
            pass
        else:
            await self._add_guild(self, guild.id)

    async def _get_user(self, user_id):
        async with self.bot.db.acquire() as conn:
            user = await conn.fetchrow(
                """SELECT * FROM users WHERE user_id = $1""",
                user_id
            )
            return user

    async def _add_user(self, user_id):
        async with self.bot.db.acquire() as conn:
            await conn.execute(
                """INSERT INTO users (user_id) VALUES ($1)""",
                user_id
            )

    async def _get_guild(self, guild_id):
        async with self.bot.db.acquire() as conn:
            user = await conn.fetchrow(
                """SELECT * FROM guilds WHERE guild_id = $1""",
                guild_id
            )
            return user

    async def _add_guild(self, guild_id):
        async with self.bot.db.acquire() as conn:
            await conn.execute(
                """INSERT INTO guilds (guild_id) VALUES ($1)""",
                guild_id
            )

def setup(bot):
    bot.add_cog(DBHelp(bot))