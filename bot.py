import os
import discord
from discord.ext import commands

# ===== CONFIG =====
GUILD_ID = 1361678640403845211  # Your server ID
UNREGISTERED_ROLE = "Unregistered"
AWAITING_ROLE = "⏳ Awaiting Approval"

# ===== BOT SETUP =====
intents = discord.Intents.default()
intents.members = True  # Needed to manage roles
bot = commands.Bot(command_prefix="!", intents=intents)

# ===== ON READY =====
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    # Sync commands for this guild only (appears instantly)
    guild = discord.Object(id=GUILD_ID)
    try:
        await bot.tree.sync(guild=guild)
        print("Slash commands synced for your server!")
    except discord.Forbidden:
        print("Warning: Could not sync slash commands. Check bot permissions.")

# ===== SLASH COMMAND =====
@bot.tree.command(guild=discord.Object(id=GUILD_ID), description="Register your Roblox username")
async def register(interaction: discord.Interaction, name: str):
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        await interaction.response.send_message("Error: Could not find the server.", ephemeral=True)
        return

    member = guild.get_member(interaction.user.id)
    if not member:
        await interaction.response.send_message("Error: Could not find you in the server.", ephemeral=True)
        return

    # Find roles
    unregistered_role = discord.utils.get(guild.roles, name=UNREGISTERED_ROLE)
    awaiting_role = discord.utils.get(guild.roles, name=AWAITING_ROLE)

    # Update nickname
    try:
        await member.edit(nick=name)
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to change your nickname.", ephemeral=True)
        return

    # Remove Unregistered role
    if unregistered_role and unregistered_role in member.roles:
        await member.remove_roles(unregistered_role)

    # Add Awaiting Approval role
    if awaiting_role and awaiting_role not in member.roles:
        await member.add_roles(awaiting_role)

    # Send confirmation
    await interaction.response.send_message(f"✅ Your username has been set to **{name}**. You now have access to the server!", ephemeral=True)

# ===== RUN BOT =====
bot.run(os.getenv("DISCORD_TOKEN"))
