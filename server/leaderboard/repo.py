from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from db.db import engine
from db.models import Climb, LeaderboardSnapshot, User


GRADE_POINTS = {
    "A": 100,
    "B": 200,
    "C": 400,
    "D": 800,
}

PERIOD_DAYS = 14
DAILY_DECAY_RATE = 0.03
MIN_DECAY_MULTIPLIER = 0.60
PERIOD_ANCHOR = datetime(1970, 1, 1, tzinfo=timezone.utc)


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _calculate_decayed_points(grade: str, effective_date: datetime, period_start: datetime) -> int:
    base_points = GRADE_POINTS.get((grade or "").upper())
    if base_points is None:
        return 0

    days_elapsed = max(0, (_ensure_utc(effective_date) - period_start).days)
    decay_multiplier = max(MIN_DECAY_MULTIPLIER, 1 - (days_elapsed * DAILY_DECAY_RATE))
    return round(base_points * decay_multiplier)


def _get_current_period_start(now_utc: datetime) -> datetime:
    period_duration = timedelta(days=PERIOD_DAYS)
    elapsed = now_utc - PERIOD_ANCHOR
    period_index = int(elapsed.total_seconds() // period_duration.total_seconds())
    return PERIOD_ANCHOR + (period_duration * period_index)


def _get_latest_period_end_with_session(session: Session):
    statement = select(func.max(LeaderboardSnapshot.period_end))
    return session.execute(statement).scalar_one_or_none()


def get_latest_period_end():
    with Session(engine) as session:
        return _get_latest_period_end_with_session(session)


def get_live_leaderboard(limit: int = 100):
    with Session(engine) as session:
        now_utc = datetime.now(timezone.utc)
        period_start = _get_current_period_start(now_utc)

        statement = (
            select(Climb.user_id, User.username, Climb.grade, Climb.effective_date)
            .join(User, User.id == Climb.user_id)
            .where(Climb.verified.is_(True))
            .where(Climb.effective_date.is_not(None))
            .where(Climb.effective_date >= period_start)
            .where(Climb.effective_date < now_utc)
        )

        rows = session.execute(statement).all()
        aggregates = {}

        for row in rows:
            points = _calculate_decayed_points(row.grade, row.effective_date, period_start)
            if points <= 0:
                continue

            user_key = str(row.user_id)
            if user_key not in aggregates:
                aggregates[user_key] = {
                    "user_id": str(row.user_id),
                    "username": row.username,
                    "total_points": 0,
                    "climb_count": 0,
                }

            aggregates[user_key]["total_points"] += points
            aggregates[user_key]["climb_count"] += 1

        ranked = sorted(
            aggregates.values(),
            key=lambda item: (-item["total_points"], -item["climb_count"], item["username"]),
        )

        return [
            {
                "user_id": row["user_id"],
                "username": row["username"],
                "period_start": period_start,
                "period_end": now_utc,
                "total_points": row["total_points"],
                "climb_count": row["climb_count"],
                "rank": rank,
            }
            for rank, row in enumerate(ranked[:limit], start=1)
        ]


def get_latest_snapshot_leaderboard(limit: int = 100):
    with Session(engine) as session:
        latest_period_end = _get_latest_period_end_with_session(session)

        if latest_period_end is None:
            return []

        statement = (
            select(LeaderboardSnapshot, User.username)
            .join(User, User.id == LeaderboardSnapshot.user_id)
            .where(LeaderboardSnapshot.period_end == latest_period_end)
            .order_by(LeaderboardSnapshot.rank.asc())
            .limit(limit)
        )

        rows = session.execute(statement).all()
        return rows
