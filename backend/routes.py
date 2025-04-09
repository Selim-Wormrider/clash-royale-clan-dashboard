from fastapi import APIRouter
from fastapi.responses import JSONResponse
from backend.database import SessionLocal
from backend.models import RiverRaceEntry
from backend.fetcher import fetch_data
import asyncio
from datetime import datetime

router = APIRouter()


@router.get("/api/clan-members")
async def get_clan_members():
    try:
        data = await fetch_data("members")
        return JSONResponse(content=data.get("items", []))
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/api/current-war")
async def get_current_war():
    try:
        data = await fetch_data("currentwar")
        return JSONResponse(content=data)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/api/war-log")
async def get_war_log():
    try:
        data = await fetch_data("warlog")
        return JSONResponse(content=data)
    except Exception as e:
        return JSON
