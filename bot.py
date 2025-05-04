from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
from steamapi_service import SteamAPIClient, get_steam_userid

load_dotenv()
print(os.getenv('APP_ID'))
bot_token = os.getenv('BOT_TOKEN')

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all(), case_insensitive=True)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.name}")
    print("Hello command executed")



bot.run(bot_token)
