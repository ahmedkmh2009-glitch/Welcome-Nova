import discord
from discord.ext import commands
from keep_alive import keep_alive
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests
from io import BytesIO
import os
import datetime

# Intents
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Env variables
TOKEN = os.environ.get("DISCORD_TOKEN")
ID_DEL_CANAL_WELCOME = int(os.environ.get("CHANNEL_WELCOME"))
GUILD_ID = int(os.environ.get("GUILD_ID"))

keep_alive()

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")

# -----------------------------------------------------
async def create_welcome_image(member):
    user = await bot.fetch_user(member.id)
    
    # Background: banner > avatar > default
    background_url = user.banner.url if user.banner else (member.avatar.url if member.avatar else member.default_avatar.url)
    response = requests.get(background_url)
    background = Image.open(BytesIO(response.content)).convert("RGBA")
    background = background.resize((900, 350))  # Más grande
    background = background.filter(ImageFilter.GaussianBlur(6))

    # Circular avatar más grande
    avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
    response = requests.get(avatar_url)
    avatar = Image.open(BytesIO(response.content)).convert("RGBA").resize((150, 150))  # Más grande
    mask = Image.new("L", avatar.size, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, avatar.size[0], avatar.size[1]), fill=255)
    avatar.putalpha(mask)
    background.paste(avatar, (50, 100), avatar)

    # Texto sobre el cuadro
    draw = ImageDraw.Draw(background)
    try:
        font_title = ImageFont.truetype("arial.ttf", 45)
        font_sub = ImageFont.truetype("arial.ttf", 32)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # Texto principal
    draw.text((220, 100), f"Welcome {user.name}!", font=font_title, fill=(255,255,255))
    draw.text((220, 160), f"We are now {member.guild.member_count}", font=font_sub, fill=(255,255,255))

    # Fecha en inglés dentro del cuadro
    joined_time = member.joined_at or discord.utils.utcnow()
    joined_str = joined_time.strftime("%B %d, %Y, %I:%M %p")  # Ej: January 9, 2026, 11:07 PM
    draw.text((220, 210), f"Joined On: {joined_str}", font=font_sub, fill=(255,255,255))

    return background

# -----------------------------------------------------
@bot.event
async def on_member_join(member):
    if member.guild.id != GUILD_ID:
        return

    channel = bot.get_channel(ID_DEL_CANAL_WELCOME)
    if not channel:
        return

    # Imagen + embed
    image = await create_welcome_image(member)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    file = discord.File(fp=buffer, filename="welcome.png")

    guild = bot.get_guild(GUILD_ID)
    embed = discord.Embed(
        title=f"Welcome to {guild.name}!",
        description=f"👋 {member.mention}, enjoy your stay at Nova Market 💜",
        color=0x9b59b6
    )
    embed.set_image(url="attachment://welcome.png")
    embed.set_footer(text="Have fun and enjoy our community!")

    await channel.send(embed=embed, file=file)

bot.run(TOKEN)
