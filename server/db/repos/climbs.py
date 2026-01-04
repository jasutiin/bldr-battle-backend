from db.models import Climb
from db.db import engine
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime

def get_climb_from_db(id: int):
  with Session(engine) as session:
    statement = select(Climb).where(Climb.id == id)
    climb = session.execute(statement).scalar_one_or_none()
    return climb


def get_climbs_by_user(user_id: int):
  with Session(engine) as session:
    statement = select(Climb).where(Climb.user_id == user_id)
    climbs = session.execute(statement).scalars().all()
    return climbs


def get_verified_climbs(num_rows: int, id: int = -1):
  with Session(engine) as session:
    statement_no_id = select(Climb).order_by(Climb.id.desc()).fetch(num_rows)
    statement_with_id = select(Climb).where(Climb.id < id).order_by(Climb.id.desc()).limit(num_rows)

    if id == -1:
      climbs = session.execute(statement_no_id).scalars().all()
    else:
      climbs = session.execute(statement_with_id).scalars().all()

    return climbs


def get_unverified_climbs():
  with Session(engine) as session:
    statement = select(Climb).where(Climb.verified == False)
    climbs = session.execute(statement).scalars().all()
    return climbs


def create_climb(user_id: int, title: str, description: str, video_url: str):
  with Session(engine) as session:
    climb = Climb(user_id=user_id, title=title, description=description, video_url=video_url)
    session.add(climb)
    session.commit()
    session.refresh(climb)
    return climb


def update_climb_verification(id: int, verified: bool):
  with Session(engine) as session:
    session.query(Climb).filter(Climb.id == id).update({"verified": verified})
    session.commit()
    statement = select(Climb).where(Climb.id == id)
    climb = session.execute(statement).scalar_one_or_none()
    return climb