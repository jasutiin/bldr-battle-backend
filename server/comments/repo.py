from sqlalchemy import select
from sqlalchemy.orm import Session

from db.db import engine
from db.models import Comment


def get_comments_by_climb(climb_id: int):
    with Session(engine) as session:
        statement = select(Comment).where(Comment.climb_id == climb_id)
        comments = session.execute(statement).scalars().all()
        return comments


def create_comment(climb_id: int, user_id: int, content: str):
    with Session(engine) as session:
        comment = Comment(climb_id=climb_id, user_id=user_id, content=content)
        session.add(comment)
        session.commit()
        session.refresh(comment)
        return comment
