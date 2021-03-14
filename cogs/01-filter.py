"""
Filter module. Moderates chat messages.
Under construction.
"""

# alt-profanity-check >= 0.24.0
from profanity_check import predict_prob
import discord
import discord.ext.commands as commands


class Filter(commands.Cog):
    """Moderation."""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name="on_message")
    async def process_message(self, message):
        """Checks a message for profanity. Currently does nothing."""
        if message.author != self.bot.user:
            prof_percent = predict_prob([message.clean_content])
            if prof_percent[0] >= 0.75:
                await message.add_reaction('😡') # Pretty strong mute candidate
            elif prof_percent[0] >= 0.5:
                await message.add_reaction('😠')
                # 'this is a f*cking censored word' gives 53%.
                # 'wrath' gives 66%.
                # Take results with a grain of salt.

    @commands.command(hidden = True,
                      brief = "Watch your profanity!",
                      help = "View a message's profanity score.\n"
                             r"Generally a score over 50% is bad.",
                      description = "Powered by alt-profanity-check 0.24.0")
    async def profanity(self, ctx, *, message):
        """Check your message's profanity score."""
        prof_percent = predict_prob([message])
        await ctx.send(f"{ctx.author.mention}, the profanity score for that"
                       f" message is {prof_percent[0]*100:.0f}%.")

def setup(bot):
    bot.add_cog(Filter(bot))
