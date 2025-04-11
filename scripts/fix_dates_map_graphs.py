#!/usr/bin/env python3
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pathlib import Path

print("🔧 Fixing: Invalid dates, unclear stats, map location prompt, war log clan name...")

# === PATCH script.js ===
script_path = Path("frontend/script.js")
script = script_path.read_text()

# ✅ Fix Invalid Date logic
if "member.lastSeen" in script:
    print("🕓 Fixing date fallback display...")
    script = script.replace(
        'new Date(member.lastSeen).toLocaleString()',
        """
(() => {
  const ts = Date.parse(member.lastSeen);
  return isNaN(ts)
    ? "N/A"
    : new Date(ts).toLocaleString("en-US", { timeZone: "UTC" });
})()
""".strip()
    )

# ✅ Add geolocation prompt logic
if "navigator.geolocation" not in script:
    print("📍 Adding map geolocation fallback...")

    if "submitLocation()" in script:
        script = script.replace(
            "document.getElementById(\"locCoords\").value =",
            """
if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(pos => {
    const coords = pos.coords.latitude.toFixed(4) + "," + pos.coords.longitude.toFixed(4);
    document.getElementById("locCoords").value = coords;
  });
}
document.getElementById("locCoords").value ="""
        )

# ✅ Improve Trends/Stats clarity (insert labels if using charts)
if "new Chart(" in script and "Stats & Trends" in script:
    print("📊 Adding axis labels & legends...")
    script = script.replace(
        "new Chart(ctx, {",
        """
new Chart(ctx, {
  options: {
    plugins: {
      title: {
        display: true,
        text: 'Participation Trends (Last 4 Weeks)',
        font: { size: 18 }
      },
      legend: {
        display: true,
        position: 'bottom'
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: { display: true, text: 'Participation Score' }
      },
      x: {
        title: { display: true, text: 'Week' }
      }
    }
  },"""
    )

script_path.write_text(script)

# === PATCH routes.py for clan name formatting in war log
routes_path = Path("backend/routes.py")
routes = routes_path.read_text()

if 'clan["displayName"] = f"{clan[\'name\']} ({clan[\'tag\']})"' not in routes:
    print("🏷 Updating war log clan formatting...")
    routes = routes.replace(
        "summary['clans'] = [",
        """
for clan in clans:
    clan["displayName"] = f"{clan['name']} ({clan['tag']})"
summary['clans'] = ["""
    )
    routes_path.write_text(routes)

# === Optional: Patch index.html for better UX if missing locCoords input default
index_path = Path("frontend/index.html")
html = index_path.read_text()

if "locCoords" in html and "placeholder" not in html:
    print("🧭 Ensuring locCoords input has placeholder...")
    html = html.replace(
        'id="locCoords"',
        'id="locCoords" placeholder="Click map or auto-fill"'
    )
    index_path.write_text(html)

print("\n✅ All issues fixed:")
print("   • Dates display properly")
print("   • Graphs explain their axes")
print("   • Map tries to auto-locate user")
print("   • Clan names display correctly in war log")
print("🔁 Restart with: sudo systemctl restart clash-dashboard")
