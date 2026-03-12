from sqlalchemy import func, select
from sqlalchemy.orm import Session

from db.db import engine
from db.models import LeaderboardSnapshot, User


def get_latest_period_end():
    with Session(engine) as session:
        statement = select(func.max(LeaderboardSnapshot.period_end))
        return session.execute(statement).scalar_one_or_none()


def get_leaderboard(limit: int = 100):
    with Session(engine) as session:
        latest_period_end = get_latest_period_end()

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
