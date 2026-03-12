from db.models import User
from db.db import engine
from sqlalchemy.orm import Session


def register_user(id, username: str):
    with Session(engine) as session:
        user = User(id=id, username=username)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user