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


def serialize_live_leaderboard_row(row):
    return {
        "user_id": row["user_id"],
        "username": row["username"],
        "period_start": row["period_start"],
        "period_end": row["period_end"],
        "total_points": row["total_points"],
        "climb_count": row["climb_count"],
        "rank": row["rank"],
    }
