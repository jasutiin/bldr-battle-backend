from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel, field_validator

from .repo import (
    count_climbs_by_user,
    create_climb,
    get_climb_from_db,
    get_climbs_by_user,
    get_unverified_climbs,
    reject_climb,
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
    offset: int = Query(0, ge=0),
):
    climbs = get_climbs_by_user(user_id, limit=limit, offset=offset)
    total = count_climbs_by_user(user_id)
    next_offset = offset + limit if offset + limit < total else None
    previous_offset = max(0, offset - limit) if offset > 0 else None

    return {
        "items": [serialize_climb(climb) for climb in climbs],
        "pagination": {
            "offset": offset,
            "limit": limit,
            "total": total,
            "has_next": next_offset is not None,
            "has_previous": previous_offset is not None,
            "next_offset": next_offset,
            "previous_offset": previous_offset,
        },
    }


@router.get("/climbs/unverified", tags=["climbs"])
async def get_admin_unverified_climbs(
    x_admin: str | None = Header(default=None),
    limit: int = Query(1, ge=1, le=25),
    cursor: str | None = Query(default=None),
):
    require_admin(x_admin)

    parsed_cursor = None
    if cursor:
        try:
            created_at_raw, climb_id_raw = cursor.split("|", maxsplit=1)
            parsed_cursor = (datetime.fromisoformat(created_at_raw), UUID(climb_id_raw))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid cursor") from exc

    climbs = get_unverified_climbs(limit=limit, cursor=parsed_cursor)
    next_cursor = None
    if climbs:
        next_cursor = f"{climbs[-1].created_at.isoformat()}|{climbs[-1].id}"

    return {
        "items": [serialize_climb(climb) for climb in climbs],
        "next_cursor": next_cursor,
    }


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


@router.patch("/climbs/{climb_id}/reject", tags=["climbs"])
async def reject_admin_climb(
    climb_id: UUID,
    x_admin: str | None = Header(default=None),
):
    require_admin(x_admin)
    updated = reject_climb(climb_id)

    if not updated:
        raise HTTPException(status_code=404, detail="Climb not found")

    return serialize_climb(updated)


@router.get("/climbs/{climb_id}", tags=["climbs"])
async def get_climb(climb_id: UUID):
    climb = get_climb_from_db(climb_id)

    if not climb:
        raise HTTPException(status_code=404, detail="Climb not found")

    return serialize_climb(climb)
