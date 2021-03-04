
import io
import re
from datetime import datetime
import random
import utils.utils as util
from utils.colorize import set_hue
from utils.colorme import shift_hue

import discord
import discord.ext.commands
import requests
import aiohttp
import asyncio
from discord.ext import commands
from discord.ext.commands import Cog
from PIL import Image, ImageEnhance


class Avatar(Cog):

    @commands.command()
    async def avatar(self, ctx):
        embed = util.Embed()
        postable = False
        if len(ctx.message.mentions) == 0:
            embed.title = f"{ctx.author.name}'s Avatar"
            embed.set_image(url = ctx.author.avatar_url_as(size=256))
            postable = True
        elif len(ctx.message.mentions) == 1:
            embed.title = f"{ctx.message.mentions[0].name}'s Avatar"
            embed.set_image(url = ctx.message.mentions[0].avatar_url_as(size=256))
            postable = True
        else:
            await ctx.send(f"{ctx.author.mention}, Slow down please! :sweat_smile: I can only handle one at a time.")
        if postable:
            await ctx.send(embed=embed)


    @commands.command()
    async def grayscale(self, ctx):
        url_regex = "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        # Get image to grayscale.
        img_in = io.BytesIO()
        if len(ctx.message.attachments) > 0:
            await ctx.message.attachments[0].save(img_in)
        elif len(ctx.message.mentions) > 0:
            await ctx.message.mentions[0].avatar_url.save(img_in)
        elif (match := re.search(url_regex, ctx.message.clean_content)):
            url = match.group()
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    img_in = io.BytesIO()
                    img_in.write(await resp.read())
                    img_in.seek(0)
        else:
            await ctx.author.avatar_url.save(img_in)

        try:
            img = Image.open(img_in)
        except:
            await ctx.send("I can't open that file! I need an image.")
            return

        converter = ImageEnhance.Color(img)
        img = converter.enhance(0)
        img_file = io.BytesIO()
        img.save(img_file, format="PNG")
        img_file.seek(0, 0)
        file = discord.File(img_file, filename="grayscale.png")
        await ctx.send(file=file)

    @commands.command(brief = "Color shifts",
                      help = "Colorizes an image. Colors go up to 360.\n" +
                             "The whole image will become shades of one color.\n" +
                             "0 is red, then cycles around until 360.",
                      usage = "([image url] or [mention]) and/or [color value]")
    async def colorize(self, ctx, *, msg = ""):
        url_regex = "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        color = None
        # Get image URL to colorize.
        img_in = io.BytesIO()
        if len(ctx.message.attachments) > 0:
            await ctx.message.attachments[0].save(img_in)
            try:
                color = int(re.sub("<@!?\d+>", "", msg)) % 360
            except:
                pass
        elif len(ctx.message.mentions) > 0:
            await ctx.message.mentions[0].avatar_url.save(img_in)
            try:
                color = int(re.sub("<@!?\d+>", "", msg)) % 360
            except:
                pass
        elif (match := re.search(url_regex, ctx.message.clean_content)):
            url = match.group()
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    img_in = io.BytesIO()
                    img_in.write(await resp.read())
                    img_in.seek(0)
            try:
                color = int(re.sub(url_regex+"|<@!?\d+>", "", msg)) % 360
            except:
                pass
        else:
            await ctx.author.avatar_url.save(img_in)
            try:
                color = int(re.sub("<@!?\d+>", "", msg)) % 360
            except:
                pass
        # If a color rotation is not specified/not detected, decide a random one.
        if color == None:
            color = random.randint(0, 360)
        # Open in Pillow.
        try:
            img = Image.open(img_in)
        except:
            await ctx.send("I can't open that file! I need an image.")
            return
        img = set_hue(img, color)
        # Now save it and ship it out!
        img_file = io.BytesIO()
        img.save(img_file, format="PNG")
        img_file.seek(0)
        file = discord.File(img_file, filename="colorme.png")
        await ctx.send(f"Hue: {color}",file=file)

    @commands.command(brief = "Color shifts",
                      help = "Colorizes an image. Colors go up to 360.\n" +
                             "Shifts all the hues!",
                      usage = "([image url] or [mention]) and/or [spin value]")
    async def colorme(self, ctx, *, msg = ""):
        url_regex = "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        color_rot = None
        # Get image URL to colorize.
        img_in = io.BytesIO()
        if len(ctx.message.attachments) > 0:
            await ctx.message.attachments[0].save(img_in)
            try:
                color_rot = int(re.sub("<@!?\d+>", "", msg)) % 360
            except:
                pass
        elif len(ctx.message.mentions) > 0:
            await ctx.message.mentions[0].avatar_url.save(img_in)
            try:
                color_rot = int(re.sub("<@!?\d+>", "", msg)) % 360
            except:
                pass
        elif (match := re.search(url_regex, ctx.message.clean_content)):
            url = match.group()
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    img_in = io.BytesIO()
                    img_in.write(await resp.read())
                    img_in.seek(0)
            try:
                color_rot = int(re.sub(url_regex+"|<@!?\d+>", "", msg)) % 360
            except:
                pass
        else:
            await ctx.author.avatar_url.save(img_in)
            try:
                color_rot = int(re.sub("<@!?\d+>", "", msg)) % 360
            except:
                pass
        # If a color rotation is not specified/not detected, decide a random one.
        if color_rot == None:
            color_rot = random.randint(0, 360)
        # Open in Pillow.
        try:
            img = Image.open(img_in)
        except:
            await ctx.send("I can't open that file! I need an image.")
            return
        img = shift_hue(img, color_rot)
        # Now save it and ship it out!
        img_file = io.BytesIO()
        img.save(img_file, format="PNG")
        img_file.seek(0, 0)
        file = discord.File(img_file, filename="colorme.png")
        await ctx.send(f"Rotation value: {color_rot}", file=file)


def setup(bot):
    bot.add_cog(Avatar())
