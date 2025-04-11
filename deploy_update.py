import os
from pathlib import Path

print("🚧 Starting full dashboard upgrade...")

# === 1. Update styles.css ===
styles = Path("frontend/styles.css").read_text()
if "youBlockhead" not in styles:
    print("🎨 Updating styles.css...")
    styles += """

@font-face {
  font-family: 'youBlockhead';
  src: url('/static/fonts/youBlockhead.ttf') format('truetype');
}

h1, .gold-title {
  font-family: 'youBlockhead', sans-serif;
  font-size: 3rem;
  color: #ffd700;
  text-shadow: 2px 2px #000;
}

h2, .white-subtitle {
  font-family: 'youBlockhead', sans-serif;
  font-size: 1.6rem;
  color: #fff;
  text-shadow: 2px 2px #000;
}

.fade-in {
  animation: fadeInUp 0.5s ease-in both;
}

@keyframes fadeInUp {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}

/* Replace refresh button */
.refresh-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.3rem;
  font-size: 1.3rem;
  filter: brightness(1.3);
  transition: transform 0.2s ease;
}
.refresh-btn:hover {
  transform: rotate(90deg);
}

#raceSummary {
  position: relative;
}
#lastUpdated {
  position: absolute;
  top: 0.5rem;
  right: 1rem;
  font-size: 0.8rem;
  color: #ccc;
}
"""
    Path("frontend/styles.css").write_text(styles)
else:
    print("✅ styles.css already updated.")

# === 2. Update script.js ===
print("🧠 Updating script.js with excusal logic, refresh icon, scroll animations...")

script = Path("frontend/script.js")
js_code = script.read_text()

# Add passcode + excuse toggle logic at bottom if missing
if "promptExcusePasscode" not in js_code:
    js_code += """

function toggleExcusal(tag) {
  const pass = prompt("Enter 4-digit leader passcode:");
  if (!pass || pass.length !== 4) {
    alert("Invalid passcode.");
    return;
  }
  fetch(`/api/toggle-excuse/${tag}?code=${pass}`, { method: "POST" })
    .then(res => res.json())
    .then(() => loadData());
}

function promptExcusePasscode(tag) {
  toggleExcusal(tag);
}
"""

script.write_text(js_code)

# === 3. Update routes.py ===
routes = Path("backend/routes.py").read_text()
if "/api/toggle-excuse/" not in routes:
    print("🔧 Adding /api/toggle-excuse route...")
    toggle_code = """

@router.post("/api/toggle-excuse/{tag}")
def toggle_excuse(tag: str, code: str = ""):
    if code != "2042":
        return JSONResponse(content={"error": "unauthorized"}, status_code=401)
    db = SessionLocal()
    entry = db.query(RiverRaceEntry).filter_by(tag=tag).order_by(RiverRaceEntry.id.desc()).first()
    if entry:
        entry.excused = not entry.excused
        db.commit()
    db.close()
    return {"status": "toggled"}
"""
    Path("backend/routes.py").write_text(routes + toggle_code)
else:
    print("✅ Excuse route already exists.")

# === 4. Update index.html ===
html = Path("frontend/index.html").read_text()
if "promptExcusePasscode" not in html:
    print("📄 Updating index.html...")
    html = html.replace(
        '<button onclick="triggerRefresh()">🔄 Refresh</button>',
        '<button class="refresh-btn" onclick="triggerRefresh()">🔄</button>'
    )
    html = html.replace(
        '<div id="lastUpdated">Last updated: ...</div>',
        '<div id="lastUpdated">Last updated: ...</div>'
    )
    if "US Map" not in html:
        html += """
<!-- Permanent Bottom: US Map Container -->
<section>
  <div class="collapsible-header">🗺 Member Map</div>
  <div class="collapsible-content">
    <div id="mapContainer" style="height: 300px; width: 100%; background: #111; color: #ccc; display: flex; align-items: center; justify-content: center;">
      🧭 US Map Placeholder — Member pins coming soon...
    </div>
  </div>
</section>
"""
    Path("frontend/index.html").write_text(html)
else:
    print("✅ index.html already patched.")

print("✅ All updates applied! Now run:")
print("   sudo systemctl restart clash-dashboard")
