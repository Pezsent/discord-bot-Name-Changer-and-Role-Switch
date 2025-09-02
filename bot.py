import os
import discord
from discord import app_commands
from discord.ext import commands

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

GUILD_ID = YOUR_GUILD_ID  # replace with your server ID

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        await tree.sync(guild=discord.Object(id=GUILD_ID))
        print("Slash commands synced for this guild!")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@tree.command(name="register", description="Register your nickname", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(name="The nickname you want to register")
async def register(interaction: discord.Interaction, name: str):
    print(f"DEBUG: /register triggered by {interaction.user} with name={name}")  # debug
    try:
        await interaction.user.edit(nick=name)
        await interaction.response.send_message(f"Nickname changed to {name}!", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don’t have permission to change your nickname.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message("⚠️ An error occurred.", ephemeral=True)
        print(f"Error while changing nickname: {e}")

bot.run(DISCORD_TOKEN)
