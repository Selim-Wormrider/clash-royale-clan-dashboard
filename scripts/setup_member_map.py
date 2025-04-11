#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import datetime
from pathlib import Path
from backend.models import Base, RiverRaceHistory
from backend.database import SessionLocal, DB_URL, engine
import psycopg2

print("📦 Starting Member Map & Stats Upgrade")

# === PATCH models.py ===
models_path = Path("backend/models.py")
models = models_path.read_text()
if "location = Column(String" not in models:
    print("📄 Adding location column to models.py...")
    models = models.replace("war_end_time = Column(DateTime", 
        "war_end_time = Column(DateTime\n    location = Column(String, default=\"\")")
    models_path.write_text(models)

# === ALTER TABLE ===
try:
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("ALTER TABLE river_race_history ADD COLUMN IF NOT EXISTS location VARCHAR;")
    conn.commit()
    cur.close()
    conn.close()
    print("🗃️ Database column 'location' added.")
except Exception as e:
    print("❌ Failed to alter table:", e)

# === PATCH routes.py ===
routes_path = Path("backend/routes.py")
routes = routes_path.read_text()
if "/api/member-locations" not in routes:
    print("🌐 Adding /api/member-locations route...")
    routes += """

@router.get("/api/member-locations")
def member_locations():
    db = SessionLocal()
    latest_week = datetime.datetime.utcnow().isocalendar()[1]
    entries = (
        db.query(RiverRaceHistory)
        .filter(RiverRaceHistory.week == latest_week)
        .all()
    )
    pins = []
    for e in entries:
        if e.location and "," in e.location:
            parts = e.location.split(",")
            try:
                lat = float(parts[0].strip())
                lng = float(parts[1].strip())
                pins.append({ "name": e.name, "lat": lat, "lng": lng })
            except:
                continue
    db.close()
    return pins
"""
    routes_path.write_text(routes)

# === PATCH script.js ===
script_path = Path("frontend/script.js")
script = script_path.read_text()

if "loadMapPins()" not in script:
    print("🧠 Adding loadMapPins() logic to script.js...")
    script = script.replace("async function loadData() {", "async function loadData() {\n  loadMapPins();")

    script += """

async function loadMapPins() {
  const data = await fetchJSON("/api/member-locations");
  const mapContainer = document.getElementById("mapContainer");
  mapContainer.innerHTML = "";
  const map = L.map(mapContainer).setView([39.8283, -98.5795], 4);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap",
    maxZoom: 18,
  }).addTo(map);

  data.forEach(member => {
    L.marker([member.lat, member.lng])
      .addTo(map)
      .bindPopup(`<b>${member.name}</b>`);
  });
}
"""

# Add "Location:" to member card info
if "Location:" not in script:
    script = script.replace(
        "Decks Used Today: ${member.decksUsedToday || 0}<br/>",
        "Decks Used Today: ${member.decksUsedToday || 0}<br/>Location: ${member.location || '—'}<br/>"
    )

script_path.write_text(script)

# === PATCH index.html for Leaflet JS ===
index_path = Path("frontend/index.html")
html = index_path.read_text()

if "leaflet.css" not in html:
    print("🌍 Adding Leaflet CDN to index.html...")
    html = html.replace("<head>", """<head>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.3/dist/leaflet.js"></script>
""")
    index_path.write_text(html)

# === PATCH styles.css for map container ===
styles_path = Path("frontend/styles.css")
styles = styles_path.read_text()

if "#mapContainer" not in styles:
    print("🎨 Adding map container styles to styles.css...")
    styles += """

#mapContainer {
  height: 400px;
  width: 100%;
  margin-top: 1rem;
  border-radius: 10px;
  overflow: hidden;
  z-index: 2;
}
"""
    styles_path.write_text(styles)

print("\n✅ Member map setup complete.")
print("🔁 Restart server with: sudo systemctl restart clash-dashboard")
print("🧪 Test in browser: http://dashboard.mycoenvy.store/api/member-locations")
print("📦 Git commit suggestion:")
print("git add . && git commit -m '🗺️ Member map + location API + extra stats on cards' && git push")
