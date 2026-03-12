def serialize_user(user):
    return {
        "id": str(user.id),
        "username": user.username,
        "created_at": user.created_at,
    }
