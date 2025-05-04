import aiohttp
import asyncio
from dotenv import load_dotenv
import os
import re


load_dotenv()
STEAM_API_KEY = os.getenv('STEAM_API_KEY')


def strip_html_tags(text):
    cleaned_text = re.sub(r'<[^>]+>', '', text)
    formatted_text = re.sub(r"\$\d+(?:\.\d{2})?", "", cleaned_text)
    res_text = re.sub(r"[-–—]\s*$", "",formatted_text).strip()

    prices = re.findall(r"\$\d+(?:\.\d{2})?", cleaned_text)
    base_price = prices[0] if len(prices) >= 2 else None
    final_price = prices[-1] if prices else None

    return res_text, base_price, final_price


def chunk_appids(appids: list[int], chunk_size:int=60):
    for idx in range(0, len(appids), chunk_size):
        yield appids[idx:idx + chunk_size]


def get_steam_userid(url: str):
    steam_url = url.strip()

    match = re.match(r"^https?://steamcommunity\.com/(id|profiles)/([^/?#]+)", steam_url)
    if match:
        return match.group(2).strip("/")

    if steam_url.isdigit() and len(steam_url) >= 17:
        return steam_url

    if re.match(r"^[a-zA-Z0-9_-]{3,32}$", steam_url):
        return steam_url


    raise ValueError("Error: Invalid URL")


def parse_deals_info(deals:list[dict]):
    res_list = []
    for deal in deals:
        title = deal.get('title', 'N/A')
        savings = float(deal.get('savings', 0))
        if savings == 0:
            continue
        normal = deal.get('normalPrice')
        sale = deal.get('salePrice')
        link = f"<https://www.cheapshark.com/redirect?dealID={deal.get('dealID', '')}>"
        info = (f"🎮 **{title}**\n"
                f"♨️ Discounted Price: ${sale} — {savings:.0f}% off\n"
                f"🧾 Original Price: ~~${normal}~~\n"
                f"💰 [Click here to view on Steam]({link})"
                )
        res_list.append(info)


    return res_list if res_list else None


class SteamAPIClient:
    def __init__(self):
        self.session = None
        self.api_key = STEAM_API_KEY
        self.base_url = r"https://api.steampowered.com"

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def __get(self, endpoint:str, params:dict):
        params["key"] = self.api_key
        url = f"{self.base_url}/{endpoint}"

        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                print(f"Request failed: {response.status}\n{response.text}")
                return None
            return await response.json()
        
    async def get_wishlist(self, steamid:str):
        endpoint = "IWishlistService/GetWishlist/v1/"
        params = {"steamid": steamid}

        data = await self.__get(endpoint, params)
        data_items = data.get("response", {}).get("items", [])
        wishlist_games = [item["appid"] for item in data_items if "appid" in item]
        return wishlist_games

    # use cheapshark api
    async def check_deals(self, appid_chunk: list[int]):
        url = "https://www.cheapshark.com/api/1.0/deals"
        params = {"storeID": 1,
                  "steamAppID": ",".join(map(str, appid_chunk)),
                  "pageSize": 60}

        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                print(f"Request Failed: {response.status}\n{response.text}")
            return await response.json()

    async def get_wishlist_deals(self, appids: list[int]) -> list[dict]:
        results = []
        job = [self.check_deals(chunk) for chunk in chunk_appids(appids)]
        chunks = await asyncio.gather(*job)
        for item in chunks:
            results.extend(item)

        return results

    async def resolve_vanity_url(self, uid:str):
        if uid.isdigit() and len(uid) >= 17:
            return uid

        resolve_url = "ISteamUser/ResolveVanityURL/v1/"
        params = {"vanityurl": uid}

        data = await self.__get(resolve_url, params=params)

        if not data:
            return None
        return data.get("response", {}).get("steamid")


if __name__ == "__main__":
    async def main():
        async with SteamAPIClient() as api_test:
            uid = "https://steamcommunity.com/profiles/"
            parsed_uid = get_steam_userid(uid)
            resolved_uid = await api_test.resolve_vanity_url(parsed_uid)
            print(resolved_uid)
            wishlist = await api_test.get_wishlist(resolved_uid)
            print(wishlist)
            deals = await api_test.get_wishlist_deals(wishlist)
            results = parse_deals_info(deals)
            for item in results:
                print(item)

    asyncio.run(main())