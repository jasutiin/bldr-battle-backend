from fastapi import APIRouter, HTTPException, Query

from .repo import get_user_by_username, search_users_by_username
from .service import serialize_user

router = APIRouter()


@router.get("/users/search", tags=["users"])
async def search_users(q: str = Query(..., min_length=1), limit: int = Query(20, ge=1, le=100)):
    users = search_users_by_username(q, limit)
    return [serialize_user(user) for user in users]


@router.get("/users/{username}", tags=["users"])
async def get_user(username: str):
    user = get_user_by_username(username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return serialize_user(user)