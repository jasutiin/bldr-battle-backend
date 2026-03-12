def serialize_leaderboard_row(snapshot, username: str):
    return {
        "id": str(snapshot.id),
        "user_id": str(snapshot.user_id),
        "username": username,
        "period_start": snapshot.period_start,
        "period_end": snapshot.period_end,
        "total_points": snapshot.total_points,
        "climb_count": snapshot.climb_count,
        "rank": snapshot.rank,
    }
