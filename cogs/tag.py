"""
Tag command for servers that do that.
"""

import datetime
import io

import asyncpg
from asyncpg.pool import create_pool
import discord
import discord.ext.commands as commands

class Tags(commands.Cog):
    """Holds tags. Inspired by Robo-Danny"""
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.group(invoke_without_command = True)
    async def tag(self, ctx, *, tagname = None):
        if tagname == None:
            await ctx.send_help(ctx.command)
        else:
            tag = await self._find_tag(ctx, tagname.lower())
            if tag:
                tagfiles = await self._get_attachments(tag['tag_id'])
                attachments = []
                for file in tagfiles:
                    tempfile = io.BytesIO()
                    tempfile.write(file['contents'])
                    tempfile.seek(0)
                    attachment = discord.File(tempfile, file['file_name'])
                    attachments.append(attachment)
                await ctx.send(tag['message'], files=attachments)
                await self._increment_uses(tag)
            else:
                await ctx.send(f"Couldn't find that tag.")
            

    @commands.guild_only()
    @tag.command()
    async def create(self, ctx, tagname, *, content = ''):
        if tagname in [cmd.name for cmd in self.walk_commands()]:
            await ctx.send(f"{ctx.author.mention}, the tag name is reserved.")
        else:
            if await self._find_tag(ctx, tagname.lower()):
                await ctx.send(f"{ctx.author.mention}, the tag is already in use!")
            else:
                await self._create_tag(ctx, tagname.lower(), content)
                await ctx.message.add_reaction('✍')

    @tag.command()
    async def delete(self, ctx, tagname):
        """Deletes the tag called 'tagname'."""
        tag_tup = await self._find_tag_or_alias(ctx, tagname.lower())
        if not tag_tup:
            await ctx.send(f"Couldn't find that tag.")
        elif ((tag_tup[1]['owner'] != ctx.author.id) or
              not ctx.author.guild_permissions.manage_messages):
            await ctx.send(f"You can't delete this tag!")
        elif tag_tup[0] == 'tag':
            await self._delete_tag(tag_tup[1])
            await ctx.message.add_reaction('🗑')
        elif tag_tup[0] == 'alias':
            await self._delete_alias(tag_tup[1])
            await ctx.message.add_reaction('🗑')
        else:
            await ctx.send(f"Hmm, can't find what you're looking for.")

    @tag.command()
    async def alias(self, ctx, aliasname, tagname):
        if tagname in [cmd.name for cmd in self.walk_commands()]:
            nameused = await self._find_tag_or_alias(ctx, aliasname)
            if not nameused:
                tag = await self._find_tag(ctx, tagname)
                if not tag:
                    await ctx.send("Couldn't find that tag.")
                else:
                    await self._create_alias(ctx, aliasname, tag)
            else:
                await ctx.send("Name already in use!")
        else:
            await ctx.send("That tag name is reserved.")





### HELPER FUNCTIONS
    async def _find_tag(self, ctx, tagname):
        """Finds a tag in the database. Resolves aliases."""
        async with self.bot.db.acquire() as connection:
            # First, fetch from the tag table.
            tag = await connection.fetchrow(
                "SELECT * FROM tags WHERE name = $1 and guild_id = $2",
                tagname, ctx.guild.id)
            if not tag:
                # If that fails, check the aliases.
                alias = await connection.fetchrow(
                    'SELECT * FROM tagaliases WHERE name = $1 and guild_id = $2', 
                    tagname, ctx.guild.id)
                if not alias:
                    # The tag doesn't exist.
                    return None
                tag = await connection.fetchrow(
                    'SELECT * FROM tags WHERE tag_id = $1', 
                    alias['referenced'])
            return tag

    async def _increment_uses(self, tag):
        """Increments the tag's uses statistic."""
        async with self.bot.db.acquire() as connection:
            await connection.execute(
                """UPDATE tags
                   SET uses = uses + 1
                   WHERE tag_id = $1""",
                tag['tag_id']
            )

    async def _find_tag_or_alias(self, ctx, tagname):
        """Finds a tag or alias in the database.
        Returns a tuple where 0 is either 'tag' or 'alias'
        and 1 is the record, or None if it doesn't exist.
        Does NOT resolve aliases.
        """
        async with self.bot.db.acquire() as connection:
            # First, fetch from the tag table.
            tag = await connection.fetchrow(
                "SELECT * FROM tags WHERE name = $1 and guild_id = $2",
                tagname, ctx.guild.id)
            if not tag:
                # If that fails, check the aliases.
                alias = await connection.fetchrow(
                    'SELECT * FROM tagaliases WHERE name = $1 and guild_id = $2', 
                    tagname, ctx.guild.id)
                if not alias:
                    # The tag doesn't exist.
                    return None
                return ('alias', alias)
            return ('tag', tag)

    async def _get_attachments(self, tag_id: int) -> list:
        """Gets attachments belonging to a tag."""
        async with self.bot.db.acquire() as connection:
            attachments = await connection.fetch(
                "SELECT * FROM tagfiles WHERE tag_id = $1",
                tag_id)
            return attachments

    async def _create_tag(self, ctx, tagname, content):
        async with self.bot.db.acquire() as connection:
            await connection.execute(
                """INSERT INTO tags (guild_id, name, message, owner, created_date)
                   VALUES ($1, $2, $3, $4, $5)""",
                ctx.guild.id, tagname, content, ctx.author.id, datetime.datetime.utcnow()
            )
            new_tag = await self._find_tag(ctx, tagname)
            # Add attachments to the table.
            for attachment in ctx.message.attachments:
                await connection.execute(
                    """INSERT INTO tagfiles (tag_id, file_name, contents)
                       VALUES ($1, $2, $3)""",
                    new_tag['tag_id'],
                    attachment.filename,
                    await attachment.read()
                )

    async def _create_alias(self, ctx, aliasname, tag):
        """Creates new alias pointing at `tag`"""
        async with self.bot.db.acquire() as conn:
            await conn.execute(
                """INSERT INTO tagaliases (name, referenced, guild_id, owner)
                   VALUES ($1, $2, $3, $4);""",
                aliasname,
                tag['tag_id'],
                ctx.guild.id,
                ctx.author.id
            )
    
    async def _delete_tag(self, tag):
        """Delete a tag, its aliases, and attachments."""
        async with self.bot.db.acquire() as conn:
            # Delete aliases.
            await conn.execute(
                """DELETE FROM tagaliases WHERE referenced = $1;""",
                tag['tag_id']
            )
            # Delete attachments
            await conn.execute(
                """DELETE FROM tagfiles WHERE tag_id = $1""",
                tag['tag_id']
            )
            # Delete the tag.
            await conn.execute(
                """DELETE FROM tags WHERE tag_id = $1""",
                tag['tag_id']
            )
        
    async def _delete_alias(self, alias):
        async with self.bot.db.acquire() as conn:
            await conn.execute(
                """DELETE FROM tagaliases WHERE alias_id = $1""",
                alias['alias_id']
            )


            
def setup(bot):
    bot.add_cog(Tags(bot,))
                
                
                


