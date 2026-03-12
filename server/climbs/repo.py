from datetime import datetime, timezone

from sqlalchemy import and_, select, update
from sqlalchemy.orm import Session

from db.db import engine
from db.models import Climb


GRADE_POINTS = {
    "A": 1,
    "B": 2,
    "C": 3,
    "D": 4,
}


def get_climb_from_db(climb_id):
    with Session(engine) as session:
        statement = select(Climb).where(Climb.id == climb_id)
        climb = session.execute(statement).scalar_one_or_none()
        return climb


def get_climbs_by_user(user_id, limit: int = 20, cursor: datetime | None = None):
    with Session(engine) as session:
        filters = [Climb.user_id == user_id]
        if cursor:
            filters.append(Climb.created_at < cursor)

        statement = (
            select(Climb)
            .where(and_(*filters))
            .order_by(Climb.created_at.desc())
            .limit(limit)
        )
        return session.execute(statement).scalars().all()


def get_unverified_climbs(limit: int = 100):
    with Session(engine) as session:
        statement = (
            select(Climb)
            .where(Climb.verified.is_(False))
            .order_by(Climb.created_at.desc())
            .limit(limit)
        )
        return session.execute(statement).scalars().all()


def create_climb(user_id, grade: str, name: str, video_url: str):
    with Session(engine) as session:
        climb = Climb(
            user_id=user_id,
            grade=grade,
            name=name,
            video_url=video_url,
        )
        session.add(climb)
        session.commit()
        session.refresh(climb)
        return climb


def verify_climb(climb_id):
    with Session(engine) as session:
        statement = select(Climb).where(Climb.id == climb_id)
        climb = session.execute(statement).scalar_one_or_none()

        if not climb:
            return None

        points = GRADE_POINTS.get((climb.grade or "").upper())
        if points is None:
            return None

        session.execute(
            update(Climb)
            .where(Climb.id == climb_id)
            .values(
                verified=True,
                points=points,
                effective_date=datetime.now(timezone.utc),
            )
        )
        session.commit()

        refreshed = session.execute(statement).scalar_one_or_none()
        return refreshed
