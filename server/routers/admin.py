from fastapi import APIRouter, Depends
from sqlalchemy.engine.base import Engine
from db import get_db

router = APIRouter()

@router.get("/admin/climbs", tags=["climbs"])
async def get_unverified_climbs(db: Engine = Depends(get_db)):
    """
    Retrieve unverified climbs for an admin's feed.
    """
    return {"climbs": "climb 1, climb 2, climb 3"}


@router.patch("/admin/climbs/{climb_id}", tags=["climbs"])
async def edit_climb(db: Engine = Depends(get_db)):
    """
    Either verify or reject a climb in the admin page.
    """
    return {"climbs": "climb 1, climb 2, climb 3"}