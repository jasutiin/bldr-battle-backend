from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel, field_validator

from .repo import (
    create_climb,
    get_climb_from_db,
    get_climbs_by_user,
    get_unverified_climbs,
    verify_climb,
)
from .service import require_admin, serialize_climb

router = APIRouter()


class ClimbCreate(BaseModel):
    user_id: UUID
    grade: Literal["A", "B", "C", "D"]
    name: str
    video_url: str

    @field_validator("grade", mode="before")
    @classmethod
    def normalize_grade(cls, value: str):
        if isinstance(value, str):
            return value.upper()
        return value


@router.post("/climbs", tags=["climbs"])
async def add_climb(climb: ClimbCreate):
    new_climb = create_climb(
        user_id=climb.user_id,
        grade=climb.grade,
        name=climb.name,
        video_url=climb.video_url,
    )

    if not new_climb:
        raise HTTPException(status_code=400, detail="Failed to create climb")

    return serialize_climb(new_climb)


@router.get("/users/{user_id}/climbs", tags=["climbs"])
async def get_user_climbs(
    user_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    cursor: datetime | None = Query(None),
):
    climbs = get_climbs_by_user(user_id, limit=limit, cursor=cursor)
    next_cursor = climbs[-1].created_at if climbs else None
    return {
        "items": [serialize_climb(climb) for climb in climbs],
        "next_cursor": next_cursor,
    }


@router.get("/climbs/unverified", tags=["climbs"])
async def get_admin_unverified_climbs(x_admin: str | None = Header(default=None)):
    require_admin(x_admin)
    climbs = get_unverified_climbs()
    return [serialize_climb(climb) for climb in climbs]


@router.patch("/climbs/{climb_id}/verify", tags=["climbs"])
async def verify_admin_climb(
    climb_id: UUID,
    x_admin: str | None = Header(default=None),
):
    require_admin(x_admin)
    updated = verify_climb(climb_id)

    if not updated:
        raise HTTPException(status_code=404, detail="Climb not found or climb grade is invalid")

    return serialize_climb(updated)


@router.get("/climbs/{climb_id}", tags=["climbs"])
async def get_climb(climb_id: UUID):
    climb = get_climb_from_db(climb_id)

    if not climb:
        raise HTTPException(status_code=404, detail="Climb not found")

    return serialize_climb(climb)
