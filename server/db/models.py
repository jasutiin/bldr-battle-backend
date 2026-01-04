from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class User(Base):
  __tablename__ = 'users'

  id = Column(Integer, primary_key=True, index=True)
  username = Column(String, unique=True, index=True)
  email = Column(String, unique=True, index=True)
  created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Climb(Base):
  __tablename__ = 'climbs'

  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(Integer, ForeignKey('users.id'))
  title = Column(String)
  description = Column(Text)
  video_url = Column(String)
  verified = Column(Boolean, default=False)
  created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Comment(Base):
  __tablename__ = 'comments'

  id = Column(Integer, primary_key=True, index=True)
  climb_id = Column(Integer, ForeignKey('climbs.id'))
  user_id = Column(Integer, ForeignKey('users.id'))
  content = Column(Text)
  created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
