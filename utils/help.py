"""Help command for Asterius."""

import discord
from discord.ext import commands
import utils.utils as util

class HelpCommand(commands.DefaultHelpCommand):
    def __init__(self, **options):
        super().__init__(**options)
        # self.command_attrs = {"usage" : "[command]",
        #                       "description" : "Sends this message.",
        #                       "aliases" : ["halp"],
        #                       "name" : "help"}
        self.command_attrs['usage'] = "[command]"

    async def send_command_help(self, command: commands.Command):
        try:
            if await command.can_run(ctx=self.context):
                embed = util.Embed()
                embed.title = self.clean_prefix + command.name
                embed.description = command.help
                if command.cog_name:
                    embed.add_field(name="Category", value=command.cog_name, 
                                    inline=False)
                if command.usage:
                    embed.add_field(name="Usage",
                                    value=self.clean_prefix + command.name + ' ' +
                                        command.usage,
                                    inline=False)
                else:
                    embed.add_field(name="Usage",
                                    value=self.clean_prefix + command.name)
                if command.aliases:
                    embed.add_field(name="Aliases", value=", ".join(command.aliases),
                                    inline=False)
                await self.get_destination().send(embed=embed)
            else:
                await self.get_destination().send("You can't run this command" +
                                                " here.")
        except commands.NotOwner:
            self.command_not_found()
        except commands.CheckFailure:
            await self.get_destination().send("You can't run this command here.")

    async def send_cog_help(self, cog):
        return super().send_cog_help(cog)
    
        
