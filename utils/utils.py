
import datetime
import config
import discord
from discord.ext import commands

class Embed(discord.Embed):
    """Embed with some prebuilt values."""
    def __init__(self):
        """Creates a new embed."""
        super().__init__()
        self.color = config.EMBED_COLOR
        self.timestamp = datetime.datetime.now()


