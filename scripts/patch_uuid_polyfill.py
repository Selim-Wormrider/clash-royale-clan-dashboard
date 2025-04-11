#!/usr/bin/env python3
import os, re
from pathlib import Path

print("🔐 Scanning for crypto.randomUUID() usage and patching with fallback...")

# === Target script ===
js_path = Path("frontend/script.js")
script = js_path.read_text()

# === Polyfill function
polyfill = """
// 🔐 UUID v4 Polyfill (browser-safe)
function generateUUID() {
  return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
    (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
  );
}
"""

# === Replace direct calls
if "crypto.randomUUID()" in script:
    print("🔁 Replacing crypto.randomUUID() with generateUUID()...")
    script = re.sub(r"crypto\.randomUUID\(\)", "generateUUID()", script)

# === Add polyfill at top (once)
if "function generateUUID()" not in script:
    print("✅ Adding generateUUID polyfill at top of script.js...")
    script = polyfill.strip() + "\n\n" + script

js_path.write_text(script)

print("\n✅ All crypto.randomUUID() calls replaced safely.")
print("🔁 Restart server: sudo systemctl restart clash-dashboard")
print("🧹 Then: Hard-refresh browser (Ctrl + Shift + R)")
