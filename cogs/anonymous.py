"""
"Anonymous Chat"
Let your players post stuff anonymously in a channel.

Credit to LegitName for the idea!
"""

import re

import discord
from discord.ext import commands

ANON_CHANNEL = 840973877269626921  # The channel where posts should go
ANON_LOG = 840975177945055302  # Where mods can see the authors
ANON_SUBMISSIONS = 841078797788643338  # All messages in this channel are posted anonymously.

class Anonymous(commands.Cog):
    """Allows anonymous posting in a channel via the bot.
    Anonymous for users, anyway - a mod can still see who posted what.
    """

    def __init__(self, bot):
        self.bot = bot
        self.authors = {}  # Becomes {msg_id : author (Member/User)}
        self.counter = counter()

        self.anon_channel = bot.get_channel(ANON_CHANNEL)
        self.anon_log = bot.get_channel(ANON_LOG)
        self.anon_submissions = bot.get_channel(ANON_SUBMISSIONS)

    def cog_check(self, ctx):
        """Only if the person can see the channel, but works wherever."""
        return ctx.author in self.anon_channel.members

    @commands.command(brief="Post an anonymous message!",
                      help="Write a message for #anonymous. To run it, use the "
                           "command by itself with no arguments, and the bot "
                           "will walk you through the rest.",
                      usage="",
                      description="Thanks LegitName for the idea!")
    async def anonymous(self, ctx, *, anything = ""):
        """Sends an anonymous message via a maker."""
        if anything:
            await ctx.send("Just use {ctx.prefix}anonymous to start.")
        else:
            prompt = await ctx.send("Ready! Please send your message you want to anonymize.")

            def check(message):
                return (message.channel == ctx.channel and
                        message.author == ctx.author)
            
            msg = await self.bot.wait_for('message', check=check)
            await self.send_anonymous_msg(msg)
            
            try:
                await prompt.delete()
                await msg.delete()
            except:
                pass
            await ctx.send("Message sent!", delete_after=10)

    async def send_anonymous_msg(self, message):
        """Takes a Message and sends it anonymously in the anonymous channel,
        including adding an ID from the counter."""
        attachments = [await attachment.to_file() for attachment in message.attachments]
        id_num = next(self.counter)
        id_str = f"`#{id_num}`\n"
        msg = await self.anon_channel.send(id_str+message.content, files=attachments)
        await self.anon_log.send(f"#{id_num} sent by {message.author}")
        await self.process_anon_mentions(msg)
        self.authors[id_num] = message.author

    async def process_anon_mentions(self, anon_msg):
        """Notifies authors of mentioned posts."""
        mentioned_ints = []
        matches = re.findall('>>(\d+)', anon_msg.content)
        # Returns `str`s so make them ints instead.
        matches = [int(num) for num in matches]
        for message in matches:  # message is an int
            if message in self.authors and message not in mentioned_ints:
                notify_txt = (f"Hey! Your message `#{message}` has been mentioned "
                              f"in the anonymous channel.\nSee {anon_msg.jump_url} "
                              "to learn more.")
                await self.authors[message].send(notify_txt)
                mentioned_ints.append(message)

    @commands.Cog.listener(name="on_reaction_add")
    async def delete_message(self, reaction, user):
        """If someone sends the trashcan emoji to their own message, it will
        be deleted. Else (trashcan but not author), 
        the reaction will be removed for anonymity.
        """
        if reaction.message.channel == self.anon_channel:
            if str(reaction) == '🗑':
                match = re.match('`#(\d+)`', reaction.message.content)
                if not match:
                    await reaction.remove(user)
                    return
                msg_id = int(match.groups[0])
                if msg_id in self.authors:
                    if self.authors[msg_id] == user:
                        await reaction.message.delete()
                        return
                await reaction.remove(user)

    @commands.Cog.listener(name="on_message")
    async def autopost_message(self, message):
        """If a message is posted in the anonymous submissions channel,
        it will be automatically posted."""
        if message.channel == self.anon_submissions:
            if message.author != self.bot.user:
                await self.send_anonymous_msg(message)
                await message.delete()
                await message.channel.send("Message sent!", delete_after=10)

def counter():
    """Generates ID numbers for posts. Starts at 10000 and continues."""
    number = 10000
    while True:
        yield number
        number += 1

def setup(bot):
    bot.add_cog(Anonymous(bot))