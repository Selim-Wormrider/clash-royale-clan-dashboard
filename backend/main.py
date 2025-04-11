from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from backend.routes import router

app = FastAPI(
    title="Bravo Six Dashboard",
    description="Clash Royale Clan War Dashboard",
    version="1.1.0"
)

# === Allow frontend access ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dashboard.mycoenvy.store"],  # Set specific domain(s) in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# === Mount static assets ===
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# === Attach API router ===
app.include_router(router)

# === Serve index.html ===
@app.get("/", response_class=FileResponse)
def get_dashboard():
    return FileResponse(Path("frontend/index.html"))

# === For manual testing only ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
