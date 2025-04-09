import os
from pathlib import Path

print("⚙️  Upgrading Clan War Dashboard...")

# == Update models.py ==
models = Path("backend/models.py").read_text()
if "last_updated" not in models:
    models += """

from sqlalchemy import DateTime
import datetime

if not hasattr(RiverRaceEntry, 'last_updated'):
    RiverRaceEntry.last_updated = Column(DateTime, default=datetime.datetime.utcnow)
"""
    Path("backend/models.py").write_text(models)
    print("✅ models.py updated with last_updated field")

# == Update database.py (to auto-create new columns) ==
db = Path("backend/database.py").read_text()
if "from backend.models import" not in db:
    db += "\nfrom backend.models import RiverRaceEntry"
    Path("backend/database.py").write_text(db)
    print("✅ database.py updated")

# == Update routes.py ==
routes = Path("backend/routes.py").read_text()

if "/api/refresh-race" not in routes:
    race_route = """

import datetime
import time
from backend.database import SessionLocal
from backend.models import RiverRaceEntry
from backend.fetcher import fetch_data

last_race_refresh = 0
last_member_refresh = 0

@router.get("/api/refresh-race")
def refresh_race_data():
    global last_race_refresh
    if time.time() - last_race_refresh < 300:  # 5 min
        return JSONResponse(content={"status": "cooldown"})
    data = fetch_data_sync("currentriverrace")
    if not data or "clan" not in data: return JSONResponse(content={"error": "no data"})
    week = f"{datetime.datetime.utcnow().isocalendar()[0]}-W{datetime.datetime.utcnow().isocalendar()[1]}"
    db = SessionLocal()
    for p in data["clan"]["participants"]:
        exists = db.query(RiverRaceEntry).filter_by(tag=p["tag"], week=week).first()
        if not exists:
            db.add(RiverRaceEntry(
                week=week, tag=p["tag"], name=p["name"],
                fame=p.get("fame", 0), decks_used=p.get("decksUsed", 0),
                decks_possible=p.get("decksUsedToday", 4), role=p.get("role", "member")
            ))
    db.commit()
    db.close()
    last_race_refresh = time.time()
    return {"status": "refreshed"}

@router.get("/api/summary")
def summary():
    db = SessionLocal()
    entries = db.query(RiverRaceEntry).all()
    summary = {}
    for e in entries:
        key = e.tag
        if key not in summary:
            summary[key] = {
                "tag": e.tag, "name": e.name, "role": e.role,
                "weeks": [], "excused": 0, "total": 0, "used": 0
            }
        summary[key]["weeks"].append(e.week)
        summary[key]["used"] += e.decks_used
        summary[key]["total"] += e.decks_possible
        if e.excused: summary[key]["excused"] += 1
    result = []
    for s in summary.values():
        pct = (s["used"] / s["total"]) * 100 if s["total"] else 0
        if s["role"] in ["coLeader", "leader"]:
            flag = "exempt"
        elif s["role"] == "elder" and pct < 70:
            flag = "demote"
        elif s["role"] == "member" and pct < 85:
            flag = "demote"
        elif s["role"] == "member" and pct >= 100 and len(s["weeks"]) >= 4:
            flag = "promote"
        else:
            flag = "ok"
        s["status"] = flag
        s["percent"] = round(pct, 1)
        result.append(s)
    return result

def fetch_data_sync(endpoint):
    import asyncio
    return asyncio.run(fetch_data(endpoint))
"""
    Path("backend/routes.py").write_text(routes + race_route)
    print("✅ routes.py updated with refresh + summary")

# == Update script.js ==
js_path = Path("frontend/script.js")
js_path.write_text("""
async function fetchJSON(endpoint) {
  const res = await fetch(endpoint);
  return await res.json();
}

async function loadData() {
  const summary = await fetchJSON("/api/summary");
  const container = document.getElementById("riverRaceData");
  container.innerHTML = "";
  summary.forEach(member => {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <div>
        <div class="card-title">${member.name}</div>
        <div class="role-badge">${member.role}</div>
      </div>
      <div>
        ${member.percent}% used (${member.used}/${member.total})
        <div class="fame-bar-container">
          <div class="fame-bar" style="width:${member.percent}%"></div>
        </div>
        <div>Status: <b>${member.status}</b></div>
      </div>
    `;
    container.appendChild(card);
  });

  document.getElementById("lastUpdated").innerText = "Last updated: " + new Date().toLocaleString();
}

function toggleMembers() {
  const el = document.getElementById("memberContainer");
  el.style.display = el.style.display === "none" ? "block" : "none";
}

function triggerRefresh() {
  fetch("/api/refresh-race").then(() => loadData());
}

window.onload = loadData;
""")
print("✅ script.js updated")

# == Update index.html ==
html = Path("frontend/index.html").read_text()
if "lastUpdated" not in html:
    html = html.replace(
        '<div id="riverRaceData">',
        '<div><button onclick="triggerRefresh()">🔄 Refresh</button> <span id="lastUpdated">Loading...</span></div>\n<div id="riverRaceData">'
    )
    Path("frontend/index.html").write_text(html)
    print("✅ index.html updated with refresh button and last updated display")

print("🎉 Upgrade complete. Restart your app with:")
print("   systemctl restart clash-dashboard")
