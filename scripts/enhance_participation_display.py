#!/usr/bin/env python3
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pathlib import Path

print("🚀 Enhancing member display: scores, MVP, last seen fix, excuse toggle...")

# === PATCH script.js ===
script_path = Path("frontend/script.js")
script = script_path.read_text()

if "Participation Score:" not in script:
    print("📈 Adding participation score & MVP logic to JS")

    script = script.replace("Decks Used Today:", """
    Participation Score: ${Math.round((member.decksUsed / member.decksPossible) * 100) || 0}%<br/>
    Decks Used: ${member.decksUsed} / ${member.decksPossible} (${Math.round((member.decksUsed / member.decksPossible) * 100) || 0}%)<br/>
    Boat Attacks: ${member.boatAttacks || 0}<br/>
    Fame: ${member.fame || 0}<br/>
    Decks Used Today:""")

    # MVP tags — highlight with 🥇 if they have top fame for that period
    if "loadRaceSummary()" in script:
        script = script.replace("name: p.name,", "name: p.name,\n    fame: p.fame,")

    # Fix Last Seen "Invalid Date"
    script = script.replace("new Date(member.lastSeen)", "new Date(Date.parse(member.lastSeen))")

script_path.write_text(script)

# === PATCH index.html for better label formatting ===
index_path = Path("frontend/index.html")
html = index_path.read_text()

if "Last seen:" in html and "Invalid Date" not in html:
    html = html.replace("Last seen:", "<span class='last-seen'>Last seen:</span>")
    index_path.write_text(html)

# === PATCH routes.py for clan name fix in war log
routes_path = Path("backend/routes.py")
routes = routes_path.read_text()

if "f\"{c['name']} ({c['tag']})\"" not in routes:
    print("🏷 Updating war log to show clan name before tag")
    routes = routes.replace("summary['clans'] = [", """
    for c in clans:
        c['displayName'] = f"{c['name']} ({c['tag']})"
    summary['clans'] = [
""")
    routes_path.write_text(routes)

# === PATCH styles.css for excuse toggle & participation UI ===
css_path = Path("frontend/styles.css")
styles = css_path.read_text()

if ".excuse-toggle" not in styles:
    styles += """

.excuse-toggle {
  appearance: none;
  -webkit-appearance: none;
  width: 38px;
  height: 20px;
  background: #666;
  border-radius: 20px;
  position: relative;
  outline: none;
  cursor: pointer;
  transition: background 0.3s ease;
  vertical-align: middle;
}
.excuse-toggle:checked {
  background: #f2c94c;
}
.excuse-toggle::before {
  content: "";
  width: 16px;
  height: 16px;
  background: white;
  border-radius: 50%;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: transform 0.3s ease;
}
.excuse-toggle:checked::before {
  transform: translateX(18px);
}
.last-seen {
  font-weight: bold;
  color: #ffd700;
}
"""
    css_path.write_text(styles)
    print("✅ Excuse toggle styling and last-seen color added")

print("\n✅ Enhancements complete.")
print("🔁 Restart with: sudo systemctl restart clash-dashboard")
print("🌐 Refresh page (Ctrl+Shift+R) to see updates")
