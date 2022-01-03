
import io
import random
import re

import aiohttp
import discord
import discord.ext.commands
import utils.utils as util
from discord.ext import commands
from discord.ext.commands import Cog
from PIL import Image, ImageEnhance, ImageFilter
from utils.colorize import set_hue
from utils.colorme import shift_hue
from utils import keygen


class Avatar(Cog):

    @commands.command(brief="Show a user's avatar",
                      usage="[@target]",
                      help="Gives you a user's avatar. If no one is mentioned,"
                           " gets your own avatar.")
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

    @commands.command(brief="Blurs an image.",
                      usage="[@user|url|attachment]",
                      help="Blurs an image. Gifs are not supported.")
    async def blur(self, ctx):
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

        img = img.filter(ImageFilter.GaussianBlur(0.02*min(img.size)))
        img_out = io.BytesIO()
        img.save(img_out, format="PNG")
        img_out.seek(0)
        file = discord.File(img_out, filename="blur.png")
        await ctx.send(file=file)

    @commands.command(brief="Turn an image grayscale.",
                      usage="[@user|url|attachment]",
                      help="Turns an image grayscale. Gifs are not supported.",
                      aliases=["greyscale"])
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

    @commands.command(brief = "Color shifts to one color",
                      help = "Colorizes an image. Colors go up to 360.\n" +
                             "The whole image will become shades of one color.\n" +
                             "0 is red, then cycles around until 360.\n" +
                             "Gifs are not supported.\n" +
                             "Default image is your avatar.",
                      usage = "[@user|url|attachment] [color value]",
                      description = "Code by unutbu")
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
        file = discord.File(img_file, filename="colorize.png")
        # await ctx.send(f"Hue: {color}",file=file)
        embed = util.Embed()
        embed.set_image(url="attachment://colorize.png")
        embed.set_footer(text=f"Hue: {color}")
        await ctx.send(embed=embed, file=file)        

    @commands.command(brief = "Color shifts all hues",
                      help = "Colorizes an image. Colors go up to 360.\n" +
                             "Shifts all the hues!\n" +
                             "Gifs are not supported. Default is your avatar.",
                      usage = "[@user|url|attachment] [spin value]",
                      description = "Code by unutbu")
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
        # await ctx.send(f"Rotation value: {color_rot}", file=file)
        embed = util.Embed()
        embed.set_image(url="attachment://colorme.png")
        embed.set_footer(text=f"Spin Value: {color_rot}")
        await ctx.send(embed=embed, file=file)

    @commands.command(brief = "KEYGEN",
        help="Makes a picture, like your avatar, rainbow shifting, just"
            "like your favorite [Big Shot]!\nAs usual, GIF inputs are not"
            "supported.\nDefault image is your avatar. Expect transparency to be lost.",
        usage = "[@user|url|attachment]",
        description="Colorshift code by unutbu"
        )
    async def keygen(self, ctx, *, msg=""):
        """Makes it rainbowy! Likely the last command before Asterius 2.0"""
        async with ctx.typing():
            await ctx.send("Takes a second, please be patient...", delete_after=15)
            url_regex = "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
            # This could really be good in a seperate function but I may have to
            # rewrite this in the future anyway :P
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
            # Make it rainbowy!
            keygenned_image = keygen.keygen(img)
            keygenned_file = discord.File(keygenned_image, filename="keygen.gif")
            # and send.
            await ctx.send("KEYGEN", file=keygenned_file)



def setup(bot):
    bot.add_cog(Avatar())
