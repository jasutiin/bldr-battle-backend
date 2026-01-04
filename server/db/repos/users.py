from db.models import User
from db.db import engine
from sqlalchemy.orm import Session
from sqlalchemy import select

def get_user(id: int):
  with Session(engine) as session:
    statement = select(User).where(User.id == id)
    user = session.execute(statement).scalar_one_or_none()
    return user