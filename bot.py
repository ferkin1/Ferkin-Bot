from dotenv import load_dotenv
import os
from discord import Intents, Forbidden
from discord.interactions import Interaction
from discord.ext import commands
from discord import app_commands
from steamapi_service import SteamAPIClient, get_steam_userid, parse_deals_info
import steam_profile_db as stpdb

load_dotenv()
bot_token = os.getenv('BOT_TOKEN')

intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!f ', intents=intents, case_insensitive=True, help_command=None)

@bot.event
async def on_ready():
    await bot.wait_until_ready()
    await bot.tree.sync()
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


@bot.tree.command(name="help", description="View available bot commands")
async def helpmenu(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send(f"**Bot Commands**\n/linksteamprofile <Steam Profile URL>:: Links your steam profile with F-Bot so that it can pull games from your Steam Wishlist (Make sure to set your Wishlist to public!)\n\n/wishlist :: Queries CheapShark API to check if your wishlisted games are on sale\n\n/unlink :: Unlinks your Steam profile from the bot.")


@bot.tree.command(name="linksteamprofile", description="Link your Steam Profile to your Discord account.")
@app_commands.describe(steam_url="Your Steam profile URL")
async def linksteamprofile(interaction: Interaction, steam_url: str):
    await interaction.response.defer(ephemeral=True)
    try:
        parsed_uid = get_steam_userid(steam_url)
        if not parsed_uid:
            await interaction.followup.send("❌ Invalid Steam Profile link.", ephemeral=True)
            return

        if parsed_uid.isdigit() and len(parsed_uid) >= 17:
            steam_id = parsed_uid
        else:
            async with SteamAPIClient() as steam_api:
                steam_id = await steam_api.resolve_vanity_url(parsed_uid)
                if not steam_id:
                    await interaction.followup.send("❌ Could not resolve Steam vanity name.", ephemeral=True)
                    return

        stpdb.link_steam_profile(str(interaction.user.id), steam_id)
        await interaction.followup.send(f"Steam Profile has been linked to your Discord account.", ephemeral=True)
    except ValueError as e:
        await interaction.followup.send(f"{e}", ephemeral=True)
        return

@bot.tree.command(name="wishlist", description="Return all wishlisted games that are on sale.")
async def wishlistdeals(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        steam_id = stpdb.get_profile(str(interaction.user.id))
        if not steam_id:
            await interaction.followup.send("❌ You haven't linked your Steam Profile with me yet! Use '/linksteamprofile <your Steam Profile URL>'.", ephemeral=True)
            return

        async with SteamAPIClient() as steam_api:
            wishlist = await steam_api.get_wishlist(steam_id)
            if not wishlist:
                await interaction.followup.send("⚠️ Your wishlist is empty or private.", ephemeral=True)
                return

            deals = await steam_api.get_wishlist_deals(wishlist)
            messages = parse_deals_info(deals)

            if not messages:
                await interaction.followup.send("🗿 No discounted games were found.", ephemeral=True)
                return

            current_chunk = ""
            for msg in messages:
                if len(current_chunk) + len(msg) + 2 > 2000:
                    await interaction.followup.send(current_chunk, ephemeral=True)
                    current_chunk = ""
                current_chunk += msg +"\n\n"

            if current_chunk:
                await interaction.followup.send(current_chunk, ephemeral=True)
    except Exception:
        await interaction.followup.send("❌‼️An error occurred.", ephemeral=True)

@bot.tree.command(name="unlinksteam", description="Unlink your Steam profile.")
async def unlinksteam(interaction: Interaction):
    try:
        await interaction.response.defer(ephemeral=True)
        discord_id = str(interaction.user.id)
        stpdb.unlink_profile(discord_id)
        await interaction.followup.send("Your account has now been unlinked from the bot.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"An error occured!\n{e}", ephemeral=True)
        return




bot.run(bot_token)
