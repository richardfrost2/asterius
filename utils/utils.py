
import datetime
import config
import discord
from discord.ext import commands

class Embed(discord.Embed):
    """Embed with some prebuilt values."""
    def __init__(self):
        super().__init__()
        self.color = config.embed_color
        self.timestamp = datetime.datetime.now()


