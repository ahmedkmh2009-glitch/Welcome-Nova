import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests
from io import BytesIO
import os
from datetime import datetime

# ================== CONFIG ==================

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID"))

# ================== FLASK ==================

app = Flask("keep_alive")

@app.route("/")
def home():
    return "Nova Market is alive"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    Thread(target=run).start()

# ================== DISCORD ==================

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ================== IMAGE (NEBULA STYLE) ==================

async def create_welcome_image(member: discord.Member):
    user = await member.guild.fetch_member(member.id)

    # Fondo (banner > avatar)
    bg_url = user.banner.url if user.banner else (
        user.avatar.url if user.avatar else user.default_avatar.url
    )

    bg = Image.open(BytesIO(requests.get(bg_url).content)).convert("RGBA")
    bg = bg.resize((900, 300))
    bg = bg.filter(ImageFilter.GaussianBlur(8))

    # Overlay oscuro
    overlay = Image.new("RGBA", bg.size, (0, 0, 0, 150))
    bg = Image.alpha_composite(bg, overlay)

    draw = ImageDraw.Draw(bg)

    # 🟣 Barra lateral Nebula
    bar = Image.new("RGBA", (18, 300), (182, 108, 255, 255))
    bg.paste(bar, (0, 0))

    # Avatar redondo grande
    avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
    avatar = Image.open(BytesIO(requests.get(avatar_url).content)).convert("RGBA")
    avatar = avatar.resize((180, 180))

    mask = Image.new("L", avatar.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 180, 180), fill=255)
    avatar.putalpha(mask)

    bg.paste(avatar, (70, 60), avatar)

    # Fuente Nebula
    try:
        font_name = ImageFont.truetype("nebula.ttf", 46)
        font_sub = ImageFont.truetype("nebula.ttf", 28)
    except:
        font_name = font_sub = ImageFont.load_default()

    draw.text((280, 110), user.display_name, font=font_name, fill="white")
    draw.text((280, 160), "WELCOME!", font=font_sub, fill=(210, 210, 210))

    return bg

# ================== EVENTS ==================

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    if member.guild.id != GUILD_ID:
        return

    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if not channel:
        return

    image = await create_welcome_image(member)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    file = discord.File(buffer, filename="welcome.png")

    joined = datetime.utcnow().strftime("%B %d, %Y %I:%M %p")

    embed = discord.Embed(
        title="Welcome System - Nova Market",
        description=(
            "**Welcome to Nova Market!**\n\n"
            f"**| User:** {member.mention}\n"
            f"**| Joined On:** {joined}"
        ),
        color=0xB66CFF
    )

    embed.set_image(url="attachment://welcome.png")

    await channel.send(embed=embed, file=file)

# ================== START ==================

keep_alive()
bot.run(TOKEN)
