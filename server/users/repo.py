from sqlalchemy import select
from sqlalchemy.orm import Session

from db.db import engine
from db.models import User


def get_user(id: int):
    with Session(engine) as session:
        statement = select(User).where(User.id == id)
        user = session.execute(statement).scalar_one_or_none()
        return user


def create_user(username: str, email: str):
    with Session(engine) as session:
        user = User(username=username, email=email)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user