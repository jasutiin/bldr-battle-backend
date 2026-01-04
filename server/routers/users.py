from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.repos.users import get_user as get_user_from_db, create_user

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: str


@router.get("/users/{user_id}", tags=["users"])
async def get_user(user_id: int):
    """
    Retrieve a user by their user Id.

    :param user_id: The Id of the user to retrieve.
    :type user_id: int
    """

    user = get_user_from_db(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at
    }


@router.post("/users", tags=["users"])
async def add_user(user: UserCreate):
    """
    Create a new user.
    """
    
    new_user = create_user(user.username, user.email)

    if not new_user:
        raise HTTPException(status_code=400, detail="Failed to create user")
    
    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "created_at": new_user.created_at
    }


@router.patch("/users/{user_id}", tags=["users"])
async def edit_user(user_id: int):
    """
    Edit an existing user's information.

    :param user_id: The Id of the user to edit.
    :type user_id: int
    """

    return {"user_id": user_id}


@router.delete("/users/{user_id}", tags=["users"])
async def delete_user(user_id: int):
    """
    Delete a user by their user Id.

    :param user_id: The Is of the user to delete.
    :type user_id: int
    """

    return {"user_id": user_id}