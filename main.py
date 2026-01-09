import discord
from discord.ext import commands
from keep_alive import keep_alive
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import requests
from io import BytesIO
import os
import time

# Intents
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Environment variables
TOKEN = os.environ.get("DISCORD_TOKEN")
ID_DEL_CANAL_WELCOME = int(os.environ.get("CHANNEL_WELCOME"))
GUILD_ID = int(os.environ.get("GUILD_ID"))

keep_alive()

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")

async def create_welcome_image(member):
    # Banner or avatar background
    user = await bot.fetch_user(member.id)
    background_url = user.banner.url if user.banner else (member.avatar.url if member.avatar else member.default_avatar.url)

    response = requests.get(background_url)
    background = Image.open(BytesIO(response.content)).convert("RGBA")
    background = background.resize((800, 300))
    background = background.filter(ImageFilter.GaussianBlur(5))

    # Circular avatar
    avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
    response = requests.get(avatar_url)
    avatar = Image.open(BytesIO(response.content)).convert("RGBA").resize((100, 100))
    mask = Image.new("L", avatar.size, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, avatar.size[0], avatar.size[1]), fill=255)
    avatar.putalpha(mask)

    background.paste(avatar, (50, 100), avatar)

    # Draw text
    draw = ImageDraw.Draw(background)
    try:
        font = ImageFont.truetype("arial.ttf", 35)
    except:
        font = ImageFont.load_default()
    draw.text((170, 120), f"Welcome {user.name}!", font=font, fill=(255,255,255))
    draw.text((170, 170), f"We are now {member.guild.member_count}", font=font, fill=(255,255,255))

    return background

def generate_text_message(member):
    timestamp = int(time.time())
    message = (
        f"## Welcome System - Nova Market\n"
        f"# Welcome to Nova Market!\n"
        f"**| User:** {member.mention}\n"
        f"**| Joined On:** <t:{timestamp}:f>"
    )
    return message

@bot.event
async def on_member_join(member):
    if member.guild.id != GUILD_ID:
        return

    channel = bot.get_channel(ID_DEL_CANAL_WELCOME)
    if not channel:
        return

    # Send text message style Nebula
    text_message = generate_text_message(member)
    await channel.send(text_message)

    # Send image + embed
    image = await create_welcome_image(member)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    file = discord.File(fp=buffer, filename="welcome.png")

    user = await bot.fetch_user(member.id)
    guild = bot.get_guild(GUILD_ID)

    embed = discord.Embed(
        title=f"Welcome to {guild.name}!",
        description=f"👋 {user.mention}, enjoy your stay at Nova Market 💜",
        color=0x9b59b6
    )
    embed.set_image(url="attachment://welcome.png")
    embed.set_footer(text="Have fun and enjoy our community!")

    await channel.send(embed=embed, file=file)

bot.run(TOKEN)
