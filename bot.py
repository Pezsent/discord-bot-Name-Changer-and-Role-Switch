import discord
from discord.ext import commands
import logging
import os

# ---------- Logging Setup ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("discord-bot")

# ---------- Intents ----------
intents = discord.Intents.default()
intents.members = True  # required for role/nickname changes

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------- Config ----------
AWAITING_APPROVAL_ROLE_ID = 1383768771952509091  # ⏳ Awaiting Approval
UNREGISTERED_ROLE_ID = 1412239619461746759      # Unregistered

# ---------- Events ----------
@bot.event
async def on_ready():
    logger.info(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    synced = await bot.tree.sync()
    logger.info(f"✅ Synced {len(synced)} global commands")


# ---------- Slash Command ----------
@bot.tree.command(name="register", description="Register with a new nickname")
async def register(interaction: discord.Interaction, nickname: str):
    member = interaction.user
    old_nick = member.nick

    try:
        # 1. Change nickname
        await member.edit(nick=nickname)
        logger.info(f"Register command used by {member} (old nick: {old_nick}) → new nick: '{nickname}'")

        # 2. Add Awaiting Approval role
        role_awaiting = interaction.guild.get_role(AWAITING_APPROVAL_ROLE_ID)
        if role_awaiting:
            await member.add_roles(role_awaiting)
            logger.info(f"✅ Added role '{role_awaiting.name}' to {member}")
        else:
            logger.warning(f"⚠️ Awaiting Approval role ID not found in guild {interaction.guild.name}")

        # 3. Remove Unregistered role
        role_unregistered = interaction.guild.get_role(UNREGISTERED_ROLE_ID)
        if role_unregistered:
            if role_unregistered in member.roles:
                await member.remove_roles(role_unregistered)
                logger.info(f"✅ Removed role '{role_unregistered.name}' from {member}")
            else:
                logger.info(f"ℹ️ {member} did not have the Unregistered role")
        else:
            logger.warning(f"⚠️ Unregistered role ID not found in guild {interaction.guild.name}")

        await interaction.response.send_message(
            f"✅ Nickname updated to **{nickname}**, roles adjusted.",
            ephemeral=True
        )

    except discord.Forbidden:
        logger.error(f"❌ Missing permissions to update nickname or roles for {member}")
        await interaction.response.send_message("❌ Bot lacks permission to change your nickname/roles.", ephemeral=True)
    except Exception as e:
        logger.exception(f"❌ Unexpected error during register command for {member}")
        await interaction.response.send_message("❌ An unexpected error occurred.", ephemeral=True)


# ---------- Run ----------
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("❌ DISCORD_TOKEN environment variable is not set in Pella!")

bot.run(DISCORD_TOKEN)
