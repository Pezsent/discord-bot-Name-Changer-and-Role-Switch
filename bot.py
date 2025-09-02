import os
import logging
import discord
from discord.ext import commands

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger("discord-bot")

# ---------------- BOT SETUP ----------------
intents = discord.Intents.default()
intents.message_content = True  # Required if you want to read messages

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- EVENTS ----------------
@bot.event
async def on_ready():
    logger.info(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()  # sync globally
        logger.info(f"✅ Synced {len(synced)} global slash commands")
    except Exception as e:
        logger.exception("❌ Failed to sync commands")

# ---------------- SLASH COMMANDS ----------------
@bot.tree.command(name="register", description="Register with a username")
async def register(interaction: discord.Interaction, username: str):
    try:
        logger.info(f"Register command used by {interaction.user} with username '{username}'")
        await interaction.response.send_message(
            f"✅ You registered with username: **{username}**",
            ephemeral=True
        )
    except Exception as e:
        logger.exception("❌ Error in /register command")
        await interaction.response.send_message("⚠️ Something went wrong. Check logs.", ephemeral=True)

# ---------------- ERROR HANDLER ----------------
@bot.event
async def on_command_error(ctx, error):
    logger.exception("❌ Command error", exc_info=error)
    await ctx.send("⚠️ An error occurred. Check console logs.")

# ---------------- RUN ----------------
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN") or "YOUR_TOKEN_HERE"
    if token == "YOUR_TOKEN_HERE":
        logger.error("❌ No token found! Set DISCORD_TOKEN environment variable.")
    else:
        bot.run(token)
