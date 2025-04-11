import os
from pathlib import Path

print("🚧 Starting war history archive deployment...")

# === Update models.py with river_race_history ===
models_file = Path("backend/models.py")
models = models_file.read_text()
if "class RiverRaceHistory" not in models:
    print("🧱 Adding RiverRaceHistory model...")
    models += """

class RiverRaceHistory(Base):
    __tablename__ = "river_race_history"
    id = Column(Integer, primary_key=True)
    week = Column(Integer)
    tag = Column(String)
    name = Column(String)
    fame = Column(Integer)
    decks_used = Column(Integer)
    decks_possible = Column(Integer)
    role = Column(String)
    excused = Column(Boolean, default=False)
    war_end_time = Column(DateTime)
    collected_at = Column(DateTime, default=datetime.datetime.utcnow)
"""
    models_file.write_text(models)

# === Create DB table if not exists ===
print("📦 Creating table if not exists...")
os.system("source venv/bin/activate && python3 -c 'from backend.models import Base; from backend.database import engine; Base.metadata.create_all(bind=engine)'")

# === Patch fetcher.py to archive snapshots ===
fetcher_file = Path("backend/fetcher.py")
fetcher = fetcher_file.read_text()

if "archive_race_snapshot" not in fetcher:
    print("💾 Adding archive_race_snapshot to fetcher.py...")
    archive_code = """

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
"""
    fetcher = fetcher.replace("from backend.models import RiverRaceEntry", "from backend.models import RiverRaceEntry, RiverRaceHistory")
    fetcher += archive_code
    fetcher_file.write_text(fetcher)

# === Patch /api/refresh-race route ===
routes_file = Path("backend/routes.py")
routes = routes_file.read_text()
if "archive_race_snapshot" not in routes:
    print("🌊 Updating /api/refresh-race to archive snapshot...")
    updated = routes.replace(
        "from backend.fetcher import fetch_data",
        "from backend.fetcher import fetch_data, archive_race_snapshot"
    )
    updated = updated.replace(
        "@router.get(\"/api/refresh-race\")",
        "@router.get(\"/api/refresh-race\")\n"
        "async def refresh_race():\n"
        "    data = await fetch_data(\"currentriverrace\")\n"
        "    archive_race_snapshot(data)\n"
        "    return {\"status\": \"refreshed\"}\n"
    )
    # Remove old function if needed
    updated = "\n".join(
        line for line in updated.splitlines()
        if not line.strip().startswith("async def refresh_race()")
    )
    routes_file.write_text(updated)

# === Patch frontend/index.html with week dropdown ===
index_html = Path("frontend/index.html")
html = index_html.read_text()
if "War Week" not in html:
    print("📄 Adding war week dropdown + moved refresh/updated...")
    html = html.replace(
        '<div class="collapsible-header" onclick="toggleSection(\'raceSummary\')">',
        '<div class="collapsible-header" onclick="toggleSection(\'raceSummary\')">\n'
        '🏆 River Race Summary\n'
        '<span style="margin-left:auto; display:flex; gap:0.5rem; align-items:center;" onclick="event.stopPropagation()">\n'
        '<label for="weekSelect" style="font-size:0.8rem; color:#ccc;">War Week:</label>\n'
        '<select id="weekSelect" onchange="changeWeek(this.value)">\n'
        '  <option value="0">Current</option>\n'
        '  <option value="1">-1 Week</option>\n'
        '  <option value="2">-2 Weeks</option>\n'
        '  <option value="3">-3 Weeks</option>\n'
        '</select>\n'
        '<button class="refresh-btn" onclick="triggerRefresh()">🔄</button>\n'
        '<span id="lastUpdated">Updated: ...</span>\n'
        '</span>'
    )
    index_html.write_text(html)

# === Patch script.js with week toggle logic ===
script_js = Path("frontend/script.js")
js = script_js.read_text()
if "changeWeek" not in js:
    print("🧠 Adding week selection logic to script.js...")
    js += """

function changeWeek(weekOffset) {
  const week = parseInt(weekOffset);
  if (week === 0) return loadData();

  fetch('/api/summary/week/' + week)
    .then(res => res.json())
    .then(data => {
      const container = document.getElementById("raceCompact");
      container.innerHTML = '';
      data.forEach(member => {
        const el = document.createElement("div");
        el.className = "card fade-in";
        el.innerHTML = \`
          <div>
            <div class="card-title">\${member.name}</div>
            <div class="role-badge">\${member.role}</div>
          </div>
          <div class="card-value">
            Fame: \${member.fame}, Decks: \${member.decks_used}/\${member.decks_possible}
          </div>
        \`;
        container.appendChild(el);
      });
    });
}
"""
    script_js.write_text(js)

# === Add /api/summary/week/{n} route ===
if "summary/week" not in routes:
    print("🔁 Adding summary/week/{n} route...")
    week_summary = """

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
"""
    routes_file.write_text(routes + week_summary)

print("✅ Complete! Now run:")
print("   sudo systemctl restart clash-dashboard")
