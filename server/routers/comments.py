from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.repos.comments import get_comments_by_climb, create_comment

router = APIRouter()

class CommentCreate(BaseModel):
    user_id: int
    content: str


@router.get("/climbs/{climb_id}/comments", tags=["comments"])
async def get_comments(climb_id: int):
    """
    Returns a list of comments for a specific climb.
    
    :param climb_id: The Id of the climb to get the comments of.
    :type climb_id: int
    """

    comments = get_comments_by_climb(climb_id)

    return [
        {
            "id": comment.id,
            "climb_id": comment.climb_id,
            "user_id": comment.user_id,
            "content": comment.content,
            "created_at": comment.created_at
        }
        for comment in comments
    ]


@router.post("/climbs/{climb_id}/comments", tags=["comments"])
async def add_comment(climb_id: int, comment: CommentCreate):
    """
    Adds a new comment to a climb.
    
    :param climb_id: The Id of the climb to add a new comment for.
    :type climb_id: int
    """
    
    new_comment = create_comment(climb_id, comment.user_id, comment.content)

    if not new_comment:
        raise HTTPException(status_code=400, detail="Failed to create comment")
    
    return {
        "id": new_comment.id,
        "climb_id": new_comment.climb_id,
        "user_id": new_comment.user_id,
        "content": new_comment.content,
        "created_at": new_comment.created_at
    }


@router.patch("/comments/{comment_id}", tags=["comments"])
async def edit_comment(comment_id: int):
    """
    Edits a comment.
    
    :param comment_id: The Id of the comment to edit.
    :type comment_id: int
    """

    return {"comment_id": comment_id}


@router.delete("/comments/{comment_id}", tags=["comments"])
async def delete_comment(comment_id: int):
    """
    Deletes a comment.
    
    :param climb_id: The Id of the comment to delete.
    :type climb_id: int
    """

    return {"comment_id": comment_id}