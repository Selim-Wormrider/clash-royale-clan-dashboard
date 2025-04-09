import datetime, time
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from backend.database import SessionLocal
from backend.models import RiverRaceEntry
from backend.fetcher import fetch_data

router = APIRouter()

last_race_refresh = 0
last_member_refresh = 0
cached_members = []

@router.get("/api/clan-members")
async def get_clan_members():
    global last_member_refresh, cached_members
    db = SessionLocal()

    try:
        if time.time() - last_member_refresh > 21600 or not cached_members:  # 6 hrs
            data = await fetch_data("members")
            if "items" in data:
                cached_members = data["items"]
                last_member_refresh = time.time()
        if not cached_members:
            return JSONResponse(content={"error": "No member data"}, status_code=500)
        return JSONResponse(content=cached_members)
    except Exception:
        return JSONResponse(content=cached_members or [], status_code=200)
    finally:
        db.close()

@router.get("/api/current-riverrace-compact")
async def get_current_riverrace_compact():
    try:
        data = await fetch_data("currentriverrace")
        clan_data = data.get("clan", {})
        leaderboard = sorted(data.get("clans", []), key=lambda x: -x.get("clanScore", 0))[:5]
        participants = sorted(clan_data.get("participants", []), key=lambda x: -x.get("fame", 0))
        logs = data.get("periodLogs", [])
        compact = {
            "sectionIndex": data.get("sectionIndex"),
            "periodType": data.get("periodType"),
            "warEndTime": data.get("warEndTime"),
            "clan": {
                "name": clan_data.get("name"),
                "fame": clan_data.get("fame"),
                "score": clan_data.get("clanScore"),
                "repairPoints": clan_data.get("repairPoints")
            },
            "leaderboard": [
                {"name": c.get("name"), "score": c.get("clanScore"), "fame": c.get("fame")}
                for c in leaderboard
            ],
            "participants": participants,
            "logs": logs
        }
        return compact
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
