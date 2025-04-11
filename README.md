# Bravo Six | Clash Royale Clan War Dashboard

This is a full-stack, open-source dashboard to track and analyze Clash Royale clan war participation, built with FastAPI, PostgreSQL, and vanilla JS.

## 🌍 Features
- River Race tracking with weekly logs
- Current war + member data from Clash API
- Promotion/demotion analysis logic (in progress)
- Excused battle tracking for leadership
- Responsive frontend with modern styling

## 🧪 Development

1. Clone the repo
2. Create a `.env` from `.env.example`
3. Run:
   ```bash
   cd backend
   uvicorn main:app --reload
<pre> 📁 /opt/dashboard ├── backend/ │ ├── routes.py ← FastAPI endpoints │ ├── fetcher.py ← Clash Royale API logic │ ├── models.py ← SQLAlchemy DB models │ ├── database.py ← DB session & engine ├── frontend/ │ ├── index.html ← Main UI │ ├── styles.css ← Theme & layout │ ├── script.js ← Data + interactivity │ ├── images/ ← Rank badges, rain │ ├── fonts/ ← youBlockhead.ttf ├── main.py ← FastAPI entrypoint ├── start_dashboard.sh ← Production launch script ├── .env ← Environment variables </pre>
