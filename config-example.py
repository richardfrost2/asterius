"""Bot config."""

from discord.enums import ActivityType

# Bot token - keep private!
token = ""
# Owner user ID - int
owner = 530420116815478794  # richardfrost#5699
# Default activity settings
activity_name = "this server"
activity_type = ActivityType.watching
# Extensions to load
extensions = ['cogs.avatar',
              'cogs.bot_mgmt',
              'cogs.fun',
              'cogs.interactions',
              'cogs.roles']
# Link to the repo for the !about command.
repo_link = "https://github.com/richardfrost2/asterius"
# Default embed color
embed_color = 0x451d93
