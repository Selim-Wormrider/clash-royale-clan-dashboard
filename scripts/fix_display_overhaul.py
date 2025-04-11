#!/usr/bin/env python3
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pathlib import Path

print("🔧 Overhauling display: fixing last seen, stats labeling, map location, and clan display...")

# === Overwrite script.js critical sections ===
script_path = Path("frontend/script.js")
script = script_path.read_text()

# 1. Patch last seen rendering
if "lastSeen" in script:
    script = script.replace(
        'Last seen: ${new Date(member.lastSeen).toLocaleString()}',
        """
Last seen: ${
  (() => {
    const ts = Date.parse(member.lastSeen);
    return isNaN(ts)
      ? "N/A"
      : new Date(ts).toLocaleString("en-US", { timeZone: "UTC" });
  })()
}
""".strip()
    )

# 2. Patch Chart.js config with axes labels
if "new Chart(ctx" in script and "scales" not in script:
    script = script.replace(
        "new Chart(ctx, {",
        """
new Chart(ctx, {
  options: {
    plugins: {
      title: {
        display: true,
        text: '4-Week Participation Trend',
        font: { size: 18 }
      },
      legend: { display: true, position: 'bottom' }
    },
    scales: {
      y: { beginAtZero: true, title: { display: true, text: 'Score (%)' } },
      x: { title: { display: true, text: 'Week #' } }
    }
  },"""
    )

# 3. Add geolocation prompt for map fallback
if "navigator.geolocation" not in script:
    script += """

window.onload = function() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(pos => {
      const latlng = pos.coords.latitude.toFixed(4) + "," + pos.coords.longitude.toFixed(4);
      const field = document.getElementById("locCoords");
      if (field && !field.value) field.value = latlng;
    });
  }
};
"""

script_path.write_text(script)
print("✅ Patched script.js")

# === Overwrite clan tag formatting in routes.py
routes_path = Path("backend/routes.py")
routes = routes_path.read_text()

if "displayName" not in routes:
    routes = routes.replace(
        "summary['clans'] = [",
        """
for clan in clans:
    clan["displayName"] = f"{clan['name']} ({clan['tag']})"
summary['clans'] = ["""
    )
    routes_path.write_text(routes)
    print("✅ Patched clan name/tag in routes.py")

# === Force placeholder in locCoords input
index_path = Path("frontend/index.html")
html = index_path.read_text()

if 'id="locCoords"' in html and "placeholder" not in html:
    html = html.replace(
        'id="locCoords"',
        'id="locCoords" placeholder="Auto-filled or click map"'
    )
    index_path.write_text(html)
    print("✅ Added placeholder to locCoords input")

print("\n✅ Display fixes deployed.")
print("🔁 Restart with: sudo systemctl restart clash-dashboard")
print("🔄 Then: Hard refresh in browser (Ctrl+Shift+R)")
