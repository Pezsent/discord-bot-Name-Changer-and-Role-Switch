import discord
from discord.ext import commands

TOKEN = "YOUR_BOT_TOKEN_HERE"  # replace with your bot token
GUILD_ID = 123456789012345678  # replace with your server's ID
UNREGISTERED_ROLE = "Unregistered"
APPROVAL_ROLE = "⏳ Awaiting Approval"

# using slash commands instead of prefix "!"
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.slash_command(guild_ids=[GUILD_ID], description="Register your name")
async def setusername(ctx, name: str):
    guild = ctx.guild
    member = ctx.author

    # remove Unregistered role if they have it
    role_unreg = discord.utils.get(guild.roles, name=UNREGISTERED_ROLE)
    if role_unreg in member.roles:
        await member.remove_roles(role_unreg)

    # give Awaiting Approval role
    role_approval = discord.utils.get(guild.roles, name=APPROVAL_ROLE)
    if role_approval:
        await member.add_roles(role_approval)

    # change nickname
    try:
        await member.edit(nick=name)
    except:
        await ctx.respond("⚠️ Couldn’t change your nickname, check my role position!", ephemeral=True)
        return

    await ctx.respond(f"✅ Name set to **{name}**. You now have the Awaiting Approval role.")

bot.run(TOKEN)

