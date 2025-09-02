import discord
from discord.ext import commands
import logging

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
AWAITING_APPROVAL_ROLE = "⏳ Awaiting Approval"   # exact role name
UNREGISTERED_ROLE = "Unregistered"               # exact role name


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
        role_awaiting = discord.utils.get(member.guild.roles, name=AWAITING_APPROVAL_ROLE)
        if role_awaiting:
            await member.add_roles(role_awaiting)
            logger.info(f"✅ Added role '{AWAITING_APPROVAL_ROLE}' to {member}")
        else:
            logger.warning(f"⚠️ Role '{AWAITING_APPROVAL_ROLE}' not found in guild {member.guild.name}")

        # 3. Remove Unregistered role
        role_unregistered = discord.utils.get(member.guild.roles, name=UNREGISTERED_ROLE)
        if role_unregistered:
            if role_unregistered in member.roles:
                await member.remove_roles(role_unregistered)
                logger.info(f"✅ Removed role '{UNREGISTERED_ROLE}' from {member}")
            else:
                logger.info(f"ℹ️ {member} did not have the '{UNREGISTERED_ROLE}' role")
        else:
            logger.warning(f"⚠️ Role '{UNREGISTERED_ROLE}' not found in guild {member.guild.name}")

        await interaction.response.send_message(
            f"✅ Nickname updated to **{nickname}** and roles adjusted.",
            ephemeral=True
        )

    except discord.Forbidden:
        logger.error(f"❌ Missing permissions to update nickname or roles for {member}")
        await interaction.response.send_message("❌ Bot does not have permission to change your nickname/roles.", ephemeral=True)
    except Exception as e:
        logger.exception(f"❌ Unexpected error during register command for {member}")
        await interaction.response.send_message("❌ An unexpected error occurred.", ephemeral=True)


# ---------- Run ----------
bot.run("YOUR_TOKEN_HERE")
