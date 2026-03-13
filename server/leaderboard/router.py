from fastapi import APIRouter, Query

from .repo import get_latest_snapshot_leaderboard, get_live_leaderboard
from .service import serialize_leaderboard_row, serialize_live_leaderboard_row

router = APIRouter()


@router.get("/leaderboard", tags=["leaderboard"])
async def leaderboard(limit: int = Query(100, ge=1, le=500)):
    rows = get_live_leaderboard(limit=limit)

    return [serialize_live_leaderboard_row(row) for row in rows]


@router.get("/leaderboard/snapshots/latest", tags=["leaderboard"])
async def latest_snapshot_leaderboard(limit: int = Query(100, ge=1, le=500)):
    rows = get_latest_snapshot_leaderboard(limit=limit)

    return [serialize_leaderboard_row(snapshot, username) for snapshot, username in rows]
