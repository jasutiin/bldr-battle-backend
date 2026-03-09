from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .repo import create_climb, get_climb_from_db, get_climbs_by_user, get_verified_climbs

router = APIRouter()


class ClimbCreate(BaseModel):
    title: str
    description: str
    video_url: str


@router.get("/users/{user_id}/climbs", tags=["climbs"])
async def get_user_climbs(user_id: int):
    climbs = get_climbs_by_user(user_id)

    return [
        {
            "id": climb.id,
            "user_id": climb.user_id,
            "title": climb.title,
            "description": climb.description,
            "video_url": climb.video_url,
            "verified": climb.verified,
            "created_at": climb.created_at,
        }
        for climb in climbs
    ]


@router.get("/climbs/{climb_id}", tags=["climbs"])
async def get_climb(climb_id: int):
    climb = get_climb_from_db(climb_id)

    if not climb:
        raise HTTPException(status_code=404, detail="Climb not found")

    return {
        "id": climb.id,
        "user_id": climb.user_id,
        "title": climb.title,
        "description": climb.description,
        "video_url": climb.video_url,
        "verified": climb.verified,
        "created_at": climb.created_at,
    }


@router.get("/feed/climbs", tags=["climbs"])
async def get_user_feed_climbs(limit: int = 15, cursor: int = -1):
    climbs = get_verified_climbs(limit, cursor)

    if not climbs:
        raise HTTPException(status_code=404, detail="Climb not found")

    new_cursor = climbs[-1].id
    return {"cursor": new_cursor, "climbs": climbs}


@router.post("/users/{user_id}/climbs", tags=["climbs"])
async def add_climb(user_id: int, climb: ClimbCreate):
    new_climb = create_climb(user_id, climb.title, climb.description, climb.video_url)

    if not new_climb:
        raise HTTPException(status_code=400, detail="Failed to create climb")

    return {
        "id": new_climb.id,
        "user_id": new_climb.user_id,
        "title": new_climb.title,
        "description": new_climb.description,
        "video_url": new_climb.video_url,
        "verified": new_climb.verified,
        "created_at": new_climb.created_at,
    }


@router.patch("/climbs/{climb_id}", tags=["climbs"])
async def edit_climb(climb_id: int):
    return {"climb_id": climb_id}


@router.delete("/climbs/{climb_id}", tags=["climbs"])
async def delete_climb(climb_id: int):
    return {"climb_id": climb_id}
