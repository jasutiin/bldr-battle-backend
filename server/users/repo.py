from sqlalchemy import select
from sqlalchemy.orm import Session

from db.db import engine
from db.models import User


def get_user_by_username(username: str):
    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        user = session.execute(statement).scalar_one_or_none()
        return user


def search_users_by_username(query: str, limit: int = 20):
    with Session(engine) as session:
        statement = (
            select(User)
            .where(User.username.ilike(f"%{query}%"))
            .order_by(User.username.asc())
            .limit(limit)
        )
        return session.execute(statement).scalars().all()


def create_user(id, username: str):
    with Session(engine) as session:
        user = User(id=id, username=username)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user