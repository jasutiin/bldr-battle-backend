from sqlalchemy import select
from sqlalchemy.orm import Session

from db.db import engine
from db.models import Climb


def get_unverified_climbs():
    with Session(engine) as session:
        statement = select(Climb).where(Climb.verified == False)
        climbs = session.execute(statement).scalars().all()
        return climbs


def update_climb_verification(id: int, verified: bool):
    with Session(engine) as session:
        session.query(Climb).filter(Climb.id == id).update({"verified": verified})
        session.commit()
        statement = select(Climb).where(Climb.id == id)
        climb = session.execute(statement).scalar_one_or_none()
        return climb
