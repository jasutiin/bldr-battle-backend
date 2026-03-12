import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class User(Base):
  __tablename__ = "users"

  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  username = Column(String, unique=True, index=True)
  created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Climb(Base):
  __tablename__ = "climbs"

  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
  grade = Column(String, nullable=False)
  name = Column(String, nullable=False)
  video_url = Column(Text, nullable=False)
  verified = Column(Boolean, default=False)
  points = Column(Integer, default=0)
  created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
  effective_date = Column(DateTime)


class LeaderboardSnapshot(Base):
  __tablename__ = "leaderboard_snapshots"

  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
  period_start = Column(DateTime, nullable=False, index=True)
  period_end = Column(DateTime, nullable=False, index=True)
  total_points = Column(Integer, nullable=False)
  climb_count = Column(Integer, nullable=False)
  rank = Column(Integer, nullable=False)
