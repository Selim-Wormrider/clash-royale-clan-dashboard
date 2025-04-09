from fastapi import FastAPI
from backend.routes import router
from backend.database import init_db

app = FastAPI(title="Clash Royale Clan Dashboard")

init_db()
app.include_router(router)

# For running locally or via systemd
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
