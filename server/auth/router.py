from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from .repo import register_user
from .service import serialize_user

router = APIRouter()


class RegisterPayload(BaseModel):
    id: UUID
    username: str


@router.post("/auth/register", tags=["auth"])
async def register(payload: RegisterPayload):
    try:
        user = register_user(payload.id, payload.username)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="User with this id or username already exists")

    return serialize_user(user)
