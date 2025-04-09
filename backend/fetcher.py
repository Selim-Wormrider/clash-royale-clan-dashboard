import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("CLASH_API_KEY")
API_BASE = os.getenv("CLASH_API")
CLAN_TAG = os.getenv("CLAN_TAG").replace("#", "%23")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

async def fetch_data(endpoint):
    url = f"{API_BASE}/clans/{CLAN_TAG}/{endpoint}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS) as resp:
            return await resp.json()
