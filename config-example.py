"""Bot config."""

from discord.enums import ActivityType

# Bot token - keep private!
TOKEN = ""
# Owner user ID - int
OWNER = 530420116815478794  # richardfrost#5699 on 2-6-21
# Activity settings
ACTIVITY_NAME = "this server"
ACTIVITY_TYPE = ActivityType.watching
# Extensions to load
EXTENSIONS = ['cogs.avatar',
              'cogs.bot_mgmt',
              'cogs.fun',
              'cogs.interactions',
              'cogs.roles']
# Link to the repo for the !about command.
REPO_LINK = "https://github.com/richardfrost2/asterius"
# Default embed color
EMBED_COLOR = 0x451d93
