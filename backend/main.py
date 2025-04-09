from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import router
from backend.database import init_db
import os

app = FastAPI(title="Clash Royale Clan Dashboard")

# Allow basic CORS (useful for frontend dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Mount static assets (frontend)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Route: Serve the HTML Dashboard UI
@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    index_path = os.path.join("frontend", "index.html")
    with open(index_path, "r") as f:
        return f.read()

# Route group: API endpoints
app.include_router(router)

# Local run option
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

