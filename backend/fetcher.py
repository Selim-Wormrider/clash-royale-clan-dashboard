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


def archive_race_snapshot(data):
    db = SessionLocal()
    clan = data.get("clan", {})
    participants = clan.get("participants", [])
    war_end = data.get("warEndTime")
    week = datetime.datetime.utcnow().isocalendar()[1]

    for p in participants:
        entry = RiverRaceHistory(
            week=week,
            tag=p["tag"],
            name=p["name"],
            fame=p.get("fame", 0),
            decks_used=p.get("decksUsed", 0),
            decks_possible=4,
            role=p.get("role", ""),
            excused=False,
            war_end_time=war_end
        )
        db.add(entry)
    db.commit()
    db.close()
