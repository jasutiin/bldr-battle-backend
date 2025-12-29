from fastapi import APIRouter

router = APIRouter()

@router.get("/users/{user_id}", tags=["users"])
async def get_user(user_id: int):
    """
    Retrieve a user by their user Id.

    :param user_id: The Id of the user to retrieve.
    :type user_id: int
    """

    return {"user_id": user_id}


@router.post("/users", tags=["users"])
async def add_user():
    """
    Create a new user.
    """

    return {"message": "created a new user!"}


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