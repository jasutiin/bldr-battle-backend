from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import and_, func, or_, select, update
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


def get_climbs_by_user(user_id, limit: int = 20, offset: int = 0):
    with Session(engine) as session:
        statement = (
            select(Climb)
            .where(Climb.user_id == user_id)
            .order_by(Climb.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return session.execute(statement).scalars().all()


def count_climbs_by_user(user_id):
    with Session(engine) as session:
        statement = select(func.count()).select_from(Climb).where(Climb.user_id == user_id)
        return session.execute(statement).scalar_one()


def get_unverified_climbs(limit: int = 1, cursor: tuple[datetime, UUID] | None = None):
    with Session(engine) as session:
        condition = and_(Climb.verified.is_(False), Climb.effective_date.is_(None))

        if cursor:
            cursor_created_at, cursor_id = cursor
            condition = and_(
                condition,
                or_(
                    Climb.created_at < cursor_created_at,
                    and_(Climb.created_at == cursor_created_at, Climb.id < cursor_id),
                ),
            )

        statement = (
            select(Climb)
            .where(condition)
            .order_by(Climb.created_at.desc())
            .order_by(Climb.id.desc())
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


def reject_climb(climb_id):
    with Session(engine) as session:
        statement = select(Climb).where(Climb.id == climb_id)
        climb = session.execute(statement).scalar_one_or_none()

        if not climb:
            return None

        session.execute(
            update(Climb)
            .where(Climb.id == climb_id)
            .values(
                verified=False,
                points=0,
                effective_date=datetime.now(timezone.utc),
            )
        )
        session.commit()

        refreshed = session.execute(statement).scalar_one_or_none()
        return refreshed
