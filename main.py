import os
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
from datetime import datetime

# ---------------- CONFIG ----------------
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID"))

FONT = "nebula.ttf"  # fuente en el mismo nivel que main.py

# ---------------- BOT ----------------
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- IMAGE ----------------
async def create_welcome_image(member: discord.Member):
    # Fondo simple oscuro con blur
    bg = Image.new("RGBA", (900, 300), (30, 30, 30, 255))
    draw = ImageDraw.Draw(bg)

    # Barra lateral morada
    bar = Image.new("RGBA", (26, 300), (182, 108, 255, 255))
    bg.paste(bar, (0, 0))

    # Avatar
    avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
    avatar_data = BytesIO(await avatar_url.read())
    avatar = Image.open(avatar_data).convert("RGBA").resize((200, 200))
    mask = Image.new("L", avatar.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 200, 200), fill=255)
    bg.paste(avatar, (70, 50), mask)

    # Texto
    font_title = ImageFont.truetype(FONT, 46)  # nombre
    font_sub = ImageFont.truetype(FONT, 28)    # "WELCOME!"

    draw.text((300, 100), member.display_name, font=font_title, fill="white")
    draw.text((300, 150), "WELCOME!", font=font_sub, fill=(210, 210, 210))

    output = BytesIO()
    bg.save(output, format="PNG")
    output.seek(0)
    return output

# ---------------- EVENTS ----------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    if member.guild.id != GUILD_ID:
        return

    joined_ts = int(member.joined_at.timestamp())

    embed = discord.Embed(
        title="Welcome System - Nova Market",
        description=(
            "**Welcome to Nova Market!**\n\n"
            f"| User: {member.mention}\n"
            f"| Joined On: <t:{joined_ts}:f>"
        ),
        color=0xB66CFF
    )

    image_file = await create_welcome_image(member)
    file = discord.File(fp=image_file, filename="welcome.png")
    embed.set_image(url="attachment://welcome.png")

    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    await channel.send(embed=embed, file=file)

# ---------------- RUN ----------------
bot.run(TOKEN)
