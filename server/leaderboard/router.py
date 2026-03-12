from fastapi import APIRouter, Query

from .repo import get_leaderboard
from .service import serialize_leaderboard_row

router = APIRouter()


@router.get("/leaderboard", tags=["leaderboard"])
async def leaderboard(limit: int = Query(100, ge=1, le=500)):
    rows = get_leaderboard(limit=limit)

    return [serialize_leaderboard_row(snapshot, username) for snapshot, username in rows]
