#!/usr/bin/env python3
import os, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

STATIC_DIR = Path("frontend/static")
FAVICON_PATH = STATIC_DIR / "favicon.ico"

print("🎨 Generating Clash-themed favicon...")

STATIC_DIR.mkdir(parents=True, exist_ok=True)

# === Create an icon (32x32) ===
img = Image.new("RGBA", (32, 32), "#0a1b46")  # Deep blue bg
draw = ImageDraw.Draw(img)
draw.ellipse((6, 6, 26, 26), fill="#ffd700")  # Gold circle
draw.text((11, 8), "C", fill="black")

img.save(FAVICON_PATH, format="ICO")
print(f"✅ Favicon saved to: {FAVICON_PATH}")

# === Patch index.html
index_path = Path("frontend/index.html")
html = index_path.read_text()

if '<link rel="icon"' not in html:
    print("🛠 Adding <link rel=\"icon\"> to index.html...")
    html = html.replace("<head>", '<head>\n  <link rel="icon" type="image/x-icon" href="/static/favicon.ico">')
    index_path.write_text(html)

print("\n✅ Favicon installation complete.")
print("🔁 Restart: sudo systemctl restart clash-dashboard")
print("🧹 Browser: Ctrl + Shift + R (hard refresh)")
print("📍 Then verify favicon appears in browser tab!")
