"""
Licensed under the MIT license.
I'll include it when I feel like it.
"""

import re

import discord
from discord.ext import commands
from discord.ext.commands.errors import *
from discord.member import Member
import discord.utils

_utils_get = discord.utils.get

def _get_from_guilds(bot, getter, argument):
    result = None
    for guild in bot.guilds:
        result = getattr(guild, getter)(argument)
        if result:
            return result
    return result

def _find_member_from_guilds(bot, key, argument):
    result = None
    for guild in bot.guilds:
        result = discord.utils.find(key, guild.members)
        if result:
            return result
    return result

class I_MemberConverter(commands.converter.MemberConverter):
    """Like the MemberConverter, but case insensitive."""

    async def convert(self, ctx, argument) -> discord.Member:
        bot = ctx.bot
        # Is an ID or a mention makes this a match containing a user ID
        match = self._get_id_match(argument) or re.match(r'<@!?([0-9]+)>$', argument)
        guild = ctx.guild
        result = None
        user_id = None
        if match is None:
            case_insensitive_key = (lambda m: m.display_name.lower() == argument.lower() or
                                    m.name.lower() == argument.lower())
            # Not a mention.
            if guild:
                result = discord.utils.find(case_insensitive_key, guild.members)
            else:
                result = _find_member_from_guilds(bot, case_insensitive_key, argument)
        else:
            user_id = int(match.group(1))
            if guild:
                result = guild.get_member(user_id) or _utils_get(ctx.message.mentions, id=user_id)
            else:
                result = _get_from_guilds(bot, 'get_member', user_id)

        if result is None:
            if guild is None:
                raise MemberNotFound(argument)

            if user_id is not None:
                result = await self.query_member_by_id(bot, guild, user_id)
            else:
                result = await self.query_member_named(guild, argument)

            if not result:
                raise MemberNotFound(argument)

        return result