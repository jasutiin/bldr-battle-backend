from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .repo import get_unverified_climbs, update_climb_verification

router = APIRouter()


class ClimbVerificationUpdate(BaseModel):
    verified: bool


@router.get("/admin/climbs", tags=["climbs"])
async def get_admin_unverified_climbs():
    climbs = get_unverified_climbs()
    return climbs


@router.patch("/admin/climbs/{climb_id}", tags=["climbs"])
async def edit_climb(climb_id: int, payload: ClimbVerificationUpdate):
    climb = update_climb_verification(climb_id, payload.verified)

    if not climb:
        raise HTTPException(status_code=404, detail="Climb not found")

    return climb
