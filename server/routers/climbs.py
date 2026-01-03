from fastapi import APIRouter, Depends
from sqlalchemy.engine.base import Engine
from db import get_db

router = APIRouter()

@router.get("/users/{user_id}/climbs", tags=["climbs"])
async def get_user_climbs(user_id: int, db: Engine = Depends(get_db)):
    """
    Retrieve all climbs for a specific user.

    :param user_id: The Id of the user whose climbs to retrieve.
    :type user_id: int
    """
    return {"getting climbs of user with user_id": user_id}


@router.get("/climbs/{climb_id}", tags=["climbs"])
async def get_climb(climb_id: int, db: Engine = Depends(get_db)):
    """
    Retrieve a climb by its climb Id.

    :param climb_id: The Id of the climb to retrieve.
    :type climb_id: int
    """
    return {"climb_id": climb_id}


@router.get("/feed/climbs", tags=["climbs"])
async def get_user_feed_climbs(db: Engine = Depends(get_db)):
    """
    Retrieve verified climbs for a user's home feed.
    """
    return {"climbs": "climb 1, climb 2, climb 3"}


@router.post("/users/{user_id}/climbs", tags=["climbs"])
async def add_climb(user_id: int, db: Engine = Depends(get_db)):
    """
    Add a new climb for a specific user.

    :param user_id: The Id of the user to add a climb for.
    :type user_id: int
    """
    return {"created a new climb with user_id": user_id}


@router.patch("/climbs/{climb_id}", tags=["climbs"])
async def edit_climb(climb_id: int, db: Engine = Depends(get_db)):
    """
    Edit an existing climb's information.

    :param climb_id: The Id of the climb to edit.
    :type climb_id: int
    """
    return {"climb_id": climb_id}


@router.delete("/climbs/{climb_id}", tags=["climbs"])
async def delete_climb(climb_id: int, db: Engine = Depends(get_db)):
    """
    Delete a climb by its climb Id.

    :param climb_id: The Id of the climb to delete.
    :type climb_id: int
    """
    return {"climb_id": climb_id}