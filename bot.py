# bot.py — debug version (drop into your repo)
import os
import asyncio
import discord
from discord.ext import commands

# ---------- CONFIG ----------
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "1361678640403845211"))
UNREGISTERED_ROLE = os.getenv("UNREGISTERED_ROLE", "Unregistered")
AWAITING_ROLE = os.getenv("AWAITING_ROLE", "⏳ Awaiting Approval")
CLEAR_GUILD_CMDS = os.getenv("CLEAR_GUILD_CMDS", "0") == "1"  # set to "1" to clear+resync once
# ----------------------------

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="?", intents=intents)

# helper to pretty-print a list
def _fmt_cmds(cmds):
    return "\n".join([f"- {c.name} (id={getattr(c, 'id', 'none')})" for c in cmds]) or "(none)"

@bot.event
async def on_ready():
    print("=== ON_READY START ===")
    print(f"Bot user: {bot.user} (id={bot.user.id})")

    # ensure we have application info (app id)
    try:
        appinfo = await bot.application_info()
        print(f"Application ID: {appinfo.id}")
    except Exception as e:
        print("Could not fetch application_info():", e)
        appinfo = None

    guild_obj = discord.Object(id=GUILD_ID)

    # optional: clear guild commands first (use only when instructed)
    if CLEAR_GUILD_CMDS:
        try:
            print("CLEAR_GUILD_CMDS=1 => clearing existing guild commands...")
            await bot.tree.clear_commands(guild=guild_obj)
            print("Cleared guild commands.")
        except Exception as e:
            print("Error clearing guild commands:", e)

    # sync to guild and list registered commands
    try:
        await bot.tree.sync(guild=guild_obj)
        print("Slash commands synced for guild.")
    except Exception as e:
        print("Error syncing commands to guild:", repr(e))

    # fetch commands from Discord for this guild (what Discord thinks exists)
    try:
        commands_list = await bot.tree.fetch_commands(guild=guild_obj)
        print("Registered commands reported by Discord for this guild:")
        print(_fmt_cmds(commands_list))
    except Exception as e:
        print("Error fetching guild commands:", e)

    print("=== ON_READY END ===")

# DEBUG: log every incoming interaction payload
@bot.event
async def on_interaction(interaction: discord.Interaction):
    try:
        data = getattr(interaction, "data", None)
        # Some interactions may be none or not commands
        print("=== INCOMING INTERACTION ===")
        print(f"type: {interaction.type}, user: {getattr(interaction.user, 'id', None)}")
        print("interaction.data:", data)
        # If present, show the name field
        if isinstance(data, dict) and "name" in data:
            print("interaction command name:", data.get("name"))
        print("app_id in interaction data (if present):", data.get("application_id") if isinstance(data, dict) else None)
        print("============================")
    except Exception as e:
        print("Error logging interaction:", e)

# actual register command (guild scoped)
@bot.tree.command(guild=discord.Object(id=GUILD_ID), description="Register your Roblox username")
async def register(interaction: discord.Interaction, username: str):
    print(f"COMMAND HANDLER: /register called by {interaction.user} username={username}")
    # ensure we respond quickly or ephemeral
    try:
        member = interaction.user
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("Error: guild not available.", ephemeral=True)
            return

        unreg = discord.utils.get(guild.roles, name=UNREGISTERED_ROLE)
        await_role = discord.utils.get(guild.roles, name=AWAITING_ROLE)

        # try to set nickname
        try:
            await member.edit(nick=username, reason="Registered via /register")
            nick_ok = True
        except Exception as e:
            nick_ok = False
            print("Failed to change nick:", e)

        # try roles
        role_ops = []
        try:
            if unreg and unreg in member.roles:
                await member.remove_roles(unreg, reason="Completed registration")
                role_ops.append(f"removed {unreg.name}")
        except Exception as e:
            print("Failed to remove unreg role:", e)

        try:
            if await_role and await_role not in member.roles:
                await member.add_roles(await_role, reason="Completed registration")
                role_ops.append(f"added {await_role.name}")
        except Exception as e:
            print("Failed to add awaiting role:", e)

        resp_parts = [f"Got username `{username}`."]
        resp_parts.append("Nickname changed." if nick_ok else "Nickname NOT changed.")
        if role_ops:
            resp_parts.append("Role ops: " + ", ".join(role_ops))
        else:
            resp_parts.append("No role changes done.")

        await interaction.response.send_message(" ".join(resp_parts), ephemeral=True)
    except Exception as e:
        print("Unhandled error inside register handler:", e)
        # try to send a response if possible
        try:
            await interaction.response.send_message("Internal error.", ephemeral=True)
        except:
            pass

if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: DISCORD_TOKEN not set in environment.")
    else:
        bot.run(TOKEN)
