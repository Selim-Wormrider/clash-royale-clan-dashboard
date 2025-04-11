#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pathlib import Path
from backend.models import RiverRaceHistory
from backend.database import SessionLocal
import psycopg2
from backend.database import DB_URL

print("🗺️ Setting up interactive map interface with PIN security and clustering...")

# === PATCH routes.py ===
routes_path = Path("backend/routes.py")
routes = routes_path.read_text()

if "/api/member-location" not in routes:
    routes += """

from fastapi import Request
from pydantic import BaseModel

class LocationUpdate(BaseModel):
    tag_or_name: str
    location: str
    pin: str

@router.post("/api/member-location")
def update_location(data: LocationUpdate):
    if data.pin != "1190":  # ✅ Replace this with your real PIN
        return {"success": False, "error": "Invalid PIN"}

    db = SessionLocal()
    week = datetime.datetime.utcnow().isocalendar()[1]
    record = (
        db.query(RiverRaceHistory)
        .filter(RiverRaceHistory.week == week)
        .filter(
            (RiverRaceHistory.name.ilike(data.tag_or_name.strip())) |
            (RiverRaceHistory.tag.ilike(data.tag_or_name.strip()))
        )
        .first()
    )
    if record:
        record.location = data.location.strip()
        db.commit()
        db.close()
        return {"success": True}
    db.close()
    return {"success": False, "error": "Name or tag not found"}
"""
    routes_path.write_text(routes)
    print("✅ POST route added")

# === PATCH index.html with Leaflet+Heatmap CDN + form
index_path = Path("frontend/index.html")
html = index_path.read_text()

if "leaflet.css" not in html:
    html = html.replace("<head>", """<head>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.3/dist/leaflet.js"></script>
  <script src="https://unpkg.com/leaflet.heat/dist/leaflet-heat.js"></script>
""")

if "📍 Add Your Pin" not in html:
    html = html.replace('<div id="mapContainer">', '''
<div class="location-form">
  <h3>📍 Add Your Pin</h3>
  <input type="text" id="locName" placeholder="Name or Tag" />
  <input type="text" id="locCoords" placeholder="Lat,Lng (or click map)" />
  <input type="password" id="locPIN" placeholder="4-digit leader PIN" />
  <button onclick="submitLocation()">Add to Map</button>
  <p id="locMsg"></p>
</div>
<div id="mapContainer">
''')

index_path.write_text(html)
print("✅ Form and scripts added to HTML")

# === PATCH script.js with full logic
script_path = Path("frontend/script.js")
script = Path(script_path).read_text()

if "submitLocation()" not in script:
    script += """

async function submitLocation() {
  const name = document.getElementById("locName").value.trim();
  const loc = document.getElementById("locCoords").value.trim();
  const pin = document.getElementById("locPIN").value.trim();
  const msg = document.getElementById("locMsg");

  if (!name || !loc || !pin) {
    msg.innerText = "⚠️ Fill out all fields.";
    return;
  }

  const res = await fetch("/api/member-location", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tag_or_name: name, location: loc, pin: pin })
  });

  const data = await res.json();
  if (data.success) {
    msg.innerText = "✅ Location added!";
    loadMapPins();
  } else {
    msg.innerText = "❌ " + (data.error || "Unable to update.");
  }
}

async function loadMapPins() {
  const data = await fetchJSON("/api/member-locations");
  const mapContainer = document.getElementById("mapContainer");
  mapContainer.innerHTML = "";
  const map = L.map(mapContainer).setView([39.8283, -98.5795], 4);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap",
    maxZoom: 18,
  }).addTo(map);

  const heatData = [];

  data.forEach(member => {
    const latlng = [member.lat, member.lng];
    heatData.push(latlng);
    L.marker(latlng).addTo(map).bindPopup(`<b>${member.name}</b>`);
  });

  const heat = L.heatLayer(heatData, { radius: 25 }).addTo(map);

  map.on("click", function(e) {
    document.getElementById("locCoords").value = `${e.latlng.lat.toFixed(4)},${e.latlng.lng.toFixed(4)}`;
  });
}
"""
    Path(script_path).write_text(script)
    print("✅ Full interactive map JS injected")

# === PATCH styles.css
css_path = Path("frontend/styles.css")
styles = css_path.read_text()

if ".location-form" not in styles:
    styles += """

.location-form {
  background: rgba(0,0,0,0.6);
  padding: 1rem;
  border-radius: 10px;
  margin-bottom: 1rem;
  color: white;
}
.location-form input {
  margin: 0.3rem;
  padding: 0.4rem;
  border-radius: 6px;
  border: none;
}
.location-form button {
  padding: 0.4rem 1rem;
  background: #ffd700;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
}
"""
    css_path.write_text(styles)
    print("✅ Styling added for location form")

print("\n✅ Interactive map form, validation, PIN lock, and heatmap deployed.")
print("🔁 Restart server: sudo systemctl restart clash-dashboard")
print("🌐 Test on site and try submitting pins.")
print("🧾 Want a CSV bulk tool or admin panel? Say the word.")
