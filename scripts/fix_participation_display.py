#!/usr/bin/env python3
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pathlib import Path

print("🛠 Applying full UI + logic enhancements...")

# === 1. PATCH styles.css for toggle ===
styles_path = Path("frontend/styles.css")
styles = styles_path.read_text()

if ".excuse-toggle" not in styles:
    print("🎨 Patching toggle switch CSS...")
    styles += """

.excuse-toggle {
  appearance: none;
  -webkit-appearance: none;
  width: 40px;
  height: 22px;
  background: #555;
  border-radius: 22px;
  position: relative;
  outline: none;
  cursor: pointer;
  transition: background 0.3s ease;
}
.excuse-toggle:checked {
  background: #ffd700;
}
.excuse-toggle::before {
  content: "";
  width: 18px;
  height: 18px;
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
"""
    styles_path.write_text(styles)

# === 2. PATCH script.js for date fallback, participation % ===
script_path = Path("frontend/script.js")
script = script_path.read_text()

if "Participation Score:" not in script:
    print("📊 Injecting deck utilization + fallback date logic...")

    # Last Seen Fix
    script = script.replace(
        "new Date(member.lastSeen).toLocaleString()",
        """
(() => {
  const ts = Date.parse(member.lastSeen);
  return isNaN(ts) ? "N/A" : new Date(ts).toLocaleString("en-US", { timeZone: "UTC" });
})()
""".strip()
    )

    # Inject Utilization Line
    if "Decks Used Today:" in script:
        script = script.replace(
            "Decks Used Today:",
            """
Participation Score: ${Math.round((member.decksUsed / member.decksPossible) * 100) || 0}%<br/>
Decks Used: ${member.decksUsed} / ${member.decksPossible}<br/>
Decks Used Today:"""
        )

    script_path.write_text(script)

# === 3. PATCH index.html (toggle input style) ===
html_path = Path("frontend/index.html")
html = html_path.read_text()

if 'type="checkbox"' in html and "excuse-toggle" not in html:
    print("✅ Ensuring excuse toggles use correct structure...")
    html = html.replace(
        'type="checkbox"',
        'type="checkbox" class="excuse-toggle"'
    )
    html_path.write_text(html)

# === 4. PATCH routes.py to show clan name before tag ===
routes_path = Path("backend/routes.py")
routes = routes_path.read_text()

if 'clan["displayName"] = f"{clan[\'name\']} ({clan[\'tag\']})"' not in routes:
    print("🏷 Adding displayName logic to war log response...")
    routes = routes.replace(
        "summary['clans'] = [",
        """
for clan in clans:
    clan["displayName"] = f"{clan['name']} ({clan['tag']})"
summary['clans'] = ["""
    )
    routes_path.write_text(routes)

print("\n✅ All enhancements applied.")
print("🔁 Restart with: sudo systemctl restart clash-dashboard")
print("🌐 Then refresh browser with Ctrl+Shift+R")
