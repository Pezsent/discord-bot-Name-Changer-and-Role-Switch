import os
import discord
from discord.ext import commands

# ---------------- CONFIG ----------------
TOKEN = os.getenv("DISCORD_TOKEN")  # read token from environment variable
GUILD_ID = 1361678640403845211      # your server ID

UNREGISTERED_ROLE = "Unregistered"
AWAITING_APPROVAL_ROLE = "⏳ Awaiting Approval"
# ----------------------------------------

intents = discord.Intents.default()
intents.members = True  # needed to manage roles and nicknames

bot = commands.Bot(command_prefix="?", intents=intents)  # prefix doesn't matter for slash commands

# ---------------- EVENTS ----------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    guild = discord.Object(id=GUILD_ID)
    
    # Sync slash commands to the guild
    await bot.tree.sync(guild=guild)
    print("Slash commands synced for your server!")

    # --- DEBUG: List all registered commands in the guild ---
    commands_list = await bot.tree.fetch_commands(guild=guild)
    print("Registered commands in this guild:")
    for cmd in commands_list:
        print(f"- {cmd.name}")

# ---------------- COMMAND ----------------
@bot.tree.command(guild=discord.Object(id=GUILD_ID), description="Register your Roblox username")
async def register(interaction: discord.Interaction, username: str):
    member = interaction.user
    guild = interaction.guild

    # Get roles
    unregistered_role = discord.utils.get(guild.roles, name=UNREGISTERED_ROLE)
    awaiting_role = discord.utils.get(guild.roles, name=AWAITING_APPROVAL_ROLE)

    # Change nickname
    try:
        await member.edit(nick=username)
    except discord.Forbidden:
        await interaction.response.send_message(
            "I do not have permission to change your nickname.", ephemeral=True
        )
        return

    # Remove unregistered role
    if unregistered_role in member.roles:
        try:
            await member.remove_roles(unregistered_role)
        except discord.Forbidden:
            pass

    # Give awaiting approval role
    if awaiting_role not in member.roles:
        try:
            await member.add_roles(awaiting_role)
        except discord.Forbidden:
            pass

    # Confirm registration
    await interaction.response.send_message(
        f"Your username has been set to **{username}**. You now have access to the server!",
        ephemeral=True
    )

# ---------------- RUN BOT ----------------
if TOKEN is None:
    print("Error: DISCORD_TOKEN environment variable not set.")
else:
    bot.run(TOKEN)
