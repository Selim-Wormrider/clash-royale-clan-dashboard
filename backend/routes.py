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


@router.post("/api/toggle-excuse/{tag}")
def toggle_excuse(tag: str, code: str = ""):
    if code != "2042":
        return JSONResponse(content={"error": "unauthorized"}, status_code=401)
    db = SessionLocal()
    entry = db.query(RiverRaceEntry).filter_by(tag=tag).order_by(RiverRaceEntry.id.desc()).first()
    if entry:
        entry.excused = not entry.excused
        db.commit()
# Mirror to history if needed
        hist = db.query(RiverRaceHistory).filter_by(tag=tag, week=entry.week).first()
        if hist:
            hist.excused = entry.excused
            db.commit()

    db.close()
    return {"status": "toggled"}


@router.get("/api/summary/week/{offset}")
def summary_by_week(offset: int):
    db = SessionLocal()
    current_week = datetime.datetime.utcnow().isocalendar()[1]
    week = current_week - offset
    entries = db.query(RiverRaceHistory).filter(RiverRaceHistory.week == week).all()
    out = []
    for e in entries:
        out.append({
            "name": e.name,
            "tag": e.tag,
            "role": e.role,
            "fame": e.fame,
            "decks_used": e.decks_used,
            "decks_possible": e.decks_possible,
            "excused": e.excused
        })
    db.close()
    return out
@router.get("/api/eligibility-report")
def eligibility_report():
    db = SessionLocal()
    week = datetime.datetime.utcnow().isocalendar()[1]
    tags = db.query(RiverRaceHistory.tag).distinct().all()
    latest = {}

    for tag_tuple in tags:
        tag = tag_tuple[0]
        latest_entry = (
            db.query(RiverRaceHistory)
            .filter_by(tag=tag, week=week)
            .order_by(RiverRaceHistory.id.desc())
            .first()
        )
        if latest_entry:
            latest[tag] = {
                "tag": tag,
                "name": latest_entry.name,
                "role": latest_entry.role,
                "promotion": latest_entry.eligiblePromotion,
                "demotion": latest_entry.atRiskDemotion,
                "excused": latest_entry.excused,
                "weeksParticipated": latest_entry.weeksParticipated,
                "weeksMissed": latest_entry.weeksMissed
            }

    db.close()
    return list(latest.values())
@router.get("/api/suggest-promotions")
def suggest_promotions():
    db = SessionLocal()
    week = datetime.datetime.utcnow().isocalendar()[1]
    entries = (
        db.query(RiverRaceHistory)
        .filter(RiverRaceHistory.week == week)
        .all()
    )

    suggestions = []
    for e in entries:
        if e.excused:
            continue
        if e.eligiblePromotion and e.role not in ["coLeader", "leader"]:
            suggestions.append({
                "tag": e.tag,
                "name": e.name,
                "currentRole": e.role,
                "suggestedRole": "elder" if e.role == "member" else "coLeader",
                "reason": "100% war participation over 4 weeks"
            })
        elif e.atRiskDemotion:
            lower = {
                "elder": "member",
                "coLeader": "elder"
            }.get(e.role)
            if lower:
                suggestions.append({
                    "tag": e.tag,
                    "name": e.name,
                    "currentRole": e.role,
                    "suggestedRole": lower,
                    "reason": f"Low war activity"
                })

    db.close()
    return suggestions
