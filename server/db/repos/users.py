from db.models import User
from db.db import engine
from sqlalchemy.orm import Session
from sqlalchemy import select

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