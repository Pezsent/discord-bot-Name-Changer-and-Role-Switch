import os
import logging
import discord
from discord.ext import commands
from discord import app_commands

# === Logging Setup ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger("discord-bot")

# === Bot Setup ===
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID", 0))  # optional: use if you want per-guild sync

intents = discord.Intents.default()
intents.members = True
intents.message_content = False  # safer for slash-only bot

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# === Role IDs ===
ROLE_AWAITING_APPROVAL = 1383768771952509091  # ⏳ Awaiting Approval

# === Event Handlers ===
@bot.event
async def on_ready():
    try:
        logger.info(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

        # Sync slash commands
        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            synced = await tree.sync(guild=guild)
            logger.info(f"✅ Synced {len(synced)} commands to guild {GUILD_ID}")
        else:
            synced = await tree.sync()
            logger.info(f"✅ Synced {len(synced)} global commands")
    except Exception as e:
        logger.exception("❌ Error during on_ready")

# === Slash Commands ===
@tree.command(name="register", description="Register with a custom username")
async def register(interaction: discord.Interaction, username: str):
    try:
        member = interaction.user
        guild = interaction.guild

        if guild is None:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        # Update nickname
        old_nick = member.nick
        await member.edit(nick=username)
        logger.info(f"Register command used by {member} (old nick: {old_nick}) → new nick: '{username}'")

        # Add Awaiting Approval role
        role = guild.get_role(ROLE_AWAITING_APPROVAL)
        if role:
            await member.add_roles(role)
            logger.info(f"✅ Added role '{role.name}' to {member}")
        else:
            logger.warning(f"⚠️ Role ID {ROLE_AWAITING_APPROVAL} not found in guild {guild.id}")

        await interaction.response.send_message(
            f"✅ Registered with username: **{username}**. A moderator will review your registration.",
            ephemeral=True
        )

    except Exception as e:
        logger.exception("❌ Error in /register command")
        await interaction.response.send_message("⚠️ An error occurred while registering. Please try again later.", ephemeral=True)

# === Run Bot ===
if not TOKEN:
    raise ValueError("❌ DISCORD_BOT_TOKEN environment variable is not set!")

bot.run(TOKEN)
