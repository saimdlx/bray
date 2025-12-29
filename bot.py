import discord
from discord.ext import commands
from config import DISCORD_TOKEN
from agent.core import Agent

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
agent = Agent()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Process commands first (if any)
    await bot.process_commands(message)

    # If not a command, pass to agent
    # We can add a check here to only reply if mentioned or in DM, 
    # but for now let's reply to everything in channels the bot is in 
    # (or maybe just if mentioned for safety in public servers).
    # For this demo, let's reply if mentioned OR if it's a DM.
    
    is_dm = isinstance(message.channel, discord.DMChannel)
    is_mentioned = bot.user in message.mentions
    
    if is_dm or is_mentioned:
        async with message.channel.typing():
            # Strip mention from content if mentioned
            content = message.content.replace(f'<@{bot.user.id}>', '').strip()
            response = await agent.process_message(content, user_id=str(message.author.id))
            await message.reply(response)

def run_bot():
    if not DISCORD_TOKEN:
        print("Error: DISCORD_TOKEN not found in .env")
        return
    bot.run(DISCORD_TOKEN)
