from fastapi import APIRouter

router = APIRouter()

@router.get("/climbs/{climb_id}/comments", tags=["comments"])
async def get_comments(climb_id: int):
    """
    Returns a list of comments for a specific climb.
    
    :param climb_id: The Id of the climb to get the comments of.
    :type climb_id: int
    """

    return {"getting comments of climb with climb_id": climb_id}


@router.post("/climbs/{climb_id}/comments", tags=["comments"])
async def add_comment(climb_id: int):
    """
    Adds a new comment to a climb.
    
    :param climb_id: The Id of the climb to add a new comment for.
    :type climb_id: int
    """

    return {"climb_id": climb_id}


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