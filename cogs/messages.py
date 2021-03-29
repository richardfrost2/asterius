"""
Messages cog by richardfrost
Licensed under the MIT License
"""

import re

import discord
from discord.ext import commands
from discord.ext.commands import Cog

import utils.utils as util

class Messages(Cog):
    """Holds listeners to react to/display messages for later use."""
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message: discord.Message):
        """Message preview"""
        MESSAGE_RE = "https:\/\/discord(?:app)?.com\/channels\/(\d+|@me)\/(\d+)\/(\d+)"
        match = re.search(MESSAGE_RE, message.clean_content)
        if match:
            message_tup = match.groups()  # guild, channel, message
            channel_id = int(message_tup[1])
            channel = self.bot.get_channel(channel_id)
            if channel:  # I have access to the channel
                try:
                    lookup_msg = await channel.fetch_message(int(message_tup[2]))
                except discord.NotFound:
                    print("Message not fetched: not found")
                    return # Message not found
                except discord.Forbidden:
                    print("Message not fetched: forbidden")
                    return # Not allowed. Might not be able to see it.
                except discord.HTTPException:
                    print("Message not fetched: httpexception")
                    return # Something else went wrong.
                # At this point lets assume we got the message and we're
                # home free.
                preview = util.Embed()
                # preview.title = "Preview"
                # preview.url = lookup_msg.jump_url
                preview.set_author(name=lookup_msg.author.display_name,
                                   icon_url=lookup_msg.author.avatar_url)
                preview.description = lookup_msg.clean_content
                preview.timestamp = lookup_msg.created_at
                if lookup_msg.guild:
                    preview.set_footer(text=f"From #{channel} in {channel.guild}",
                                       icon_url=lookup_msg.guild.icon_url)
                else:
                    preview.set_footer(text=f"From {channel}",
                                       icon_url=channel.recipient.avatar_url)
                await message.channel.send(embed=preview)

    @Cog.listener(name="on_reaction_add")
    async def notepad_save(self, reaction, user):
        if str(reaction) != "🗒️":
            return
        else:
            msg = reaction.message
            embed = util.Embed()
            embed.set_author(name=msg.author.display_name,
                             icon_url=msg.author.avatar_url)
            embed.description = msg.clean_content
            embed.timestamp = msg.created_at
            if msg.guild:
                embed.set_footer(text=f"From #{msg.channel} in {msg.guild}",
                                 icon_url=msg.guild.icon_url)
            else:
                embed.set_footer(text=f"From {msg.channel}",
                                 icon_url=msg.channel.recipient.avatar_url)
            embed.add_field(name="Jump to post",
                            value=f"[Original Message]({msg.jump_url})")
            await user.send(embed=embed)

def setup(bot):
    bot.add_cog(Messages(bot))
