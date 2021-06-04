"""Just some fun bot reacts."""

import discord
from discord.ext import commands

class BotReactions(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name="on_message")
    async def react_e(self, message):
        """Respond to people saying `e` or `E` with the
        :regional_indicator_e: react. (\U0001f1ea or '🇪')"""
        if discord.utils.remove_markdown(message.content) in ('e', 'E', '🇪'):
            await message.add_reaction("\U0001f1ea")

def setup(bot):
    bot.add_cog(BotReactions(bot))