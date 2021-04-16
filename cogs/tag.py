"""
Tag command for servers that do that.
"""

import datetime
import io

import asyncpg
from asyncpg.pool import create_pool
import discord
import discord.ext.commands as commands
import utils.converters as conv
import utils.utils as util

class Tags(commands.Cog):
    """Holds tags. Inspired by Robo-Danny"""
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.group(invoke_without_command = True,
                    brief="Say whatever!",
                    help="Entry to the tag system. Without a subcommand, "
                         "displays a tag in the database.",
                    usage="<tag>")
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
    @tag.command(brief="Create a tag!",
                 help="Creates a tag of your choice! To make a multi-word tag "
                      "name, surround your tag name in quotes. It even works "
                      "with attachments!",
                 usage="<tagname> <content>")
    async def create(self, ctx, tagname, *, content = ''):
        if tagname in [cmd.name for cmd in self.walk_commands()]:
            await ctx.send(f"{ctx.author.mention}, the tag name is reserved.")
        else:
            if await self._find_tag(ctx, tagname.lower()):
                await ctx.send(f"{ctx.author.mention}, the tag is already in use!")
            else:
                await self._create_tag(ctx, tagname.lower(), content)
                await ctx.message.add_reaction('✍')

    @commands.guild_only()
    @tag.command(brief="Delete a tag.",
                 help="Removes a tag or alias from the database. You must "
                      "either own the object or have manage messages "
                      "permissions to do so.",
                 usage="<tagname>")
    async def delete(self, ctx, tagname):
        """Deletes the tag called 'tagname'."""
        tag_tup = await self._find_tag_or_alias(ctx, tagname.lower())
        if not tag_tup:
            await ctx.send(f"Couldn't find that tag.")
        elif ((tag_tup[1]['owner'] != ctx.author.id) and
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

    @commands.guild_only()
    @tag.command(brief="Creates a tag alias",
                 help="Create an alias, allowing a tag to be looked up by "
                      "another name. Use quotes around multi-word tag names.",
                 usage="<alias name> <tag name>")
    async def alias(self, ctx, aliasname, tagname):
        if tagname in [cmd.name for cmd in self.walk_commands()]:
            nameused = await self._find_tag_or_alias(ctx, aliasname)
            if not nameused:
                tag = await self._find_tag(ctx, tagname)
                if not tag:
                    await ctx.send("Couldn't find that tag.")
                else:
                    await self._create_alias(ctx, aliasname, tag)
                    await ctx.add_reaction('✍')
            else:
                await ctx.send("Name already in use!")
        else:
            await ctx.send("That tag name is reserved.")

    @commands.guild_only()
    @tag.command(brief="Transfers a tag/alias",
                 help="Transfers a tag or alias to someone else. The other "
                      "person must confirm the transfer.",
                 usage="<member> <tag name>")
    async def transfer(self, ctx, member: conv.I_MemberConverter, tagname):
        """Transfers a tag to another member."""
        tag_tup = await self._find_tag_or_alias(ctx, tagname)
        if not tag_tup:
            await ctx.send("Couldn't find the tag to transfer.")
        elif not (tag_tup[1]['owner'] == ctx.author.id):
            await ctx.send("You don't own that tag!")
        else:
            await ctx.send(f"Trying to send the tag {tagname} to {member.display_name}...",
                           delete_after=15)
            prompt = (f"{ctx.author.display_name} wants to give you ownership of "
                      f"the {tag_tup[0]} {tagname} in {ctx.guild.name}. "
                      "Will you accept?")
            if (await util.confirm(ctx, 
                                   target_user=member,
                                   channel= await member.create_dm(),
                                   prompt=prompt,
                                   timeout=120)):
                if tag_tup[0] == 'tag':
                    await self._transfer_tag(tag_tup[1], member.id)
                else:
                    await self._transfer_alias(tag_tup[1], member.id)
                await ctx.message.add_reaction('✉')
            else:
                # Confirmation box returned False
                await ctx.reply("Transfer failed - either the confirmation "
                                "was rejected or timed out.",
                                delete_after=15)

    @tag.command(brief="Get tag information",
                 help="Get information about a tag, like who owns it, how "
                      "many times it's been used, or what the alias points "
                      "to.",
                 usage="<tagname>")
    async def info(self, ctx, tagname):
        """Gets info about a tag."""
        tag_tup = await self._find_tag_or_alias(ctx, tagname)
        if not tag_tup:
            await ctx.send("Couldn't find that tag.")
        else:
            embed = util.Embed()
            owner = ctx.guild.get_member(tag_tup[1]['owner'])
            if owner:
                embed.set_author(name=owner.display_name,
                                 icon_url=owner.avatar_url)
            else:
                default_avvie = 'https://cdn.discordapp.com/embed/avatars/0.png'
                embed.set_author(name="(User not in guild)",
                                 icon_url=default_avvie)
            embed.title = tag_tup[1]['name']
            if tag_tup[0] == 'tag':
                embed.add_field(name="Tag Owner", value=f"<@{tag_tup[1]['owner']}>")
                embed.add_field(name="Uses", value=tag_tup[1]['uses'])
                embed.set_footer(text="Tag created on")
                embed.timestamp = tag_tup[1]['created_date']
            else:
                embed.add_field(name="Alias Owner", value=f"<@{tag_tup[1]['owner']}>")
                tag = await self._find_tag(ctx, tagname)
                embed.add_field(name="Referenced tag", value=tag['name'])
            await ctx.send(embed=embed)

        





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

    async def _transfer_tag(self, tag, new_owner_id):
        async with self.bot.db.acquire() as conn:
            await conn.execute(
                """UPDATE tags SET owner = $1
                   WHERE tag_id = $2""",
                new_owner_id,
                tag['tag_id']
            )
    
    async def _transfer_alias(self, alias, new_owner_id):
        async with self.bot.db.acquire() as conn:
            await conn.execute(
                """UPDATE tagaliases SET owner = $1
                   WHERE alias_id = $2""",
                new_owner_id,
                alias['alias_id']
            )


            
def setup(bot):
    bot.add_cog(Tags(bot,))
                
                
                


