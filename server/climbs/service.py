from fastapi import HTTPException


def require_admin(x_admin: str | None):
    if x_admin is None or x_admin.lower() != "true":
        raise HTTPException(status_code=403, detail="Admin access required")


def serialize_climb(climb):
    return {
        "id": str(climb.id),
        "user_id": str(climb.user_id),
        "grade": climb.grade,
        "name": climb.name,
        "video_url": climb.video_url,
        "verified": climb.verified,
        "points": climb.points,
        "created_at": climb.created_at,
        "effective_date": climb.effective_date,
    }
