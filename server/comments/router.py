from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .repo import create_comment, get_comments_by_climb

router = APIRouter()


class CommentCreate(BaseModel):
    user_id: int
    content: str


@router.get("/climbs/{climb_id}/comments", tags=["comments"])
async def get_comments(climb_id: int):
    comments = get_comments_by_climb(climb_id)

    return [
        {
            "id": comment.id,
            "climb_id": comment.climb_id,
            "user_id": comment.user_id,
            "content": comment.content,
            "created_at": comment.created_at,
        }
        for comment in comments
    ]


@router.post("/climbs/{climb_id}/comments", tags=["comments"])
async def add_comment(climb_id: int, comment: CommentCreate):
    new_comment = create_comment(climb_id, comment.user_id, comment.content)

    if not new_comment:
        raise HTTPException(status_code=400, detail="Failed to create comment")

    return {
        "id": new_comment.id,
        "climb_id": new_comment.climb_id,
        "user_id": new_comment.user_id,
        "content": new_comment.content,
        "created_at": new_comment.created_at,
    }


@router.patch("/comments/{comment_id}", tags=["comments"])
async def edit_comment(comment_id: int):
    return {"comment_id": comment_id}


@router.delete("/comments/{comment_id}", tags=["comments"])
async def delete_comment(comment_id: int):
    return {"comment_id": comment_id}
