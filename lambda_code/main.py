import os
import boto3
import logging
import time
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

GRADE_POINTS = {
    "A": 100,
    "B": 200,
    "C": 400,
    "D": 800,
}

PERIOD_DAYS = 14
DAILY_DECAY_RATE = 0.03
MIN_DECAY_MULTIPLIER = 0.60
PERIOD_ANCHOR = datetime(1970, 1, 1, tzinfo=timezone.utc)

def get_db_url():
    if os.environ.get("LOCAL_DEV"):
        return os.environ["DATABASE_URL"]

    ssm = boto3.client("ssm")
    param = ssm.get_parameter(
        Name="/boulderbattle/db_pooler_url",
        WithDecryption=True
    )
    return param["Parameter"]["Value"]

def get_db_session():
    url = get_db_url()
    engine = create_engine(url, poolclass=NullPool)
    Session = sessionmaker(bind=engine)
    return Session(), engine


def ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def calculate_decayed_points(grade: str, effective_date: datetime, period_start: datetime) -> int:
    base_points = GRADE_POINTS.get((grade or "").upper())
    if base_points is None:
        return 0

    days_elapsed = max(0, (ensure_utc(effective_date) - period_start).days)
    decay_multiplier = max(MIN_DECAY_MULTIPLIER, 1 - (days_elapsed * DAILY_DECAY_RATE))
    return round(base_points * decay_multiplier)


def get_latest_snapshot_period_end(session):
    result = session.execute(text("SELECT MAX(period_end) AS latest_period_end FROM leaderboard_snapshots"))
    return result.scalar_one_or_none()


def get_current_period_start(now_utc: datetime) -> datetime:
    period_duration = timedelta(days=PERIOD_DAYS)
    elapsed = now_utc - PERIOD_ANCHOR
    period_index = int(elapsed.total_seconds() // period_duration.total_seconds())
    return PERIOD_ANCHOR + (period_duration * period_index)


def snapshot_exists(session, period_end: datetime) -> bool:
    result = session.execute(
        text("SELECT COUNT(*) FROM leaderboard_snapshots WHERE period_end = :period_end"),
        {"period_end": period_end},
    )
    return result.scalar_one() > 0


def determine_snapshot_period(session, now_utc: datetime):
    current_period_start = get_current_period_start(now_utc)
    previous_period_end = current_period_start
    previous_period_start = previous_period_end - timedelta(days=PERIOD_DAYS)

    if snapshot_exists(session, previous_period_end):
        return None

    return previous_period_start, previous_period_end

def aggregate_and_rank(session, period_start, period_end):
    rows = session.execute(text("""
        SELECT user_id, grade, effective_date
        FROM climbs
        WHERE verified = true
        AND effective_date >= :start
        AND effective_date < :end
    """), {"start": period_start, "end": period_end})

    aggregates = {}

    for row in rows:
        points = calculate_decayed_points(row.grade, row.effective_date, period_start)
        if points <= 0:
            continue

        if row.user_id not in aggregates:
            aggregates[row.user_id] = {"total_points": 0, "climb_count": 0}

        aggregates[row.user_id]["total_points"] += points
        aggregates[row.user_id]["climb_count"] += 1

    ranked = sorted(
        aggregates.items(),
        key=lambda item: (-item[1]["total_points"], -item[1]["climb_count"], str(item[0])),
    )

    return [
        {
            "user_id": user_id,
            "total_points": stats["total_points"],
            "climb_count": stats["climb_count"],
        }
        for user_id, stats in ranked[:100]
    ]

def write_snapshots(session, results, period_start, period_end):
    rows = [
        {
            "user_id": str(row["user_id"]),
            "period_start": period_start,
            "period_end": period_end,
            "total_points": row["total_points"],
            "climb_count": row["climb_count"],
            "rank": rank
        }
        for rank, row in enumerate(results, start=1)
    ]

    session.execute(text("""
        INSERT INTO leaderboard_snapshots
            (user_id, period_start, period_end, total_points, climb_count, rank)
        VALUES
            (:user_id, :period_start, :period_end, :total_points, :climb_count, :rank)
    """), rows)

def lambda_handler(event, context):
    MAX_RETRIES = 3
    RETRY_DELAY = 2

    now_utc = datetime.now(timezone.utc)

    session = None
    engine = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            session, engine = get_db_session()

            period = determine_snapshot_period(session, now_utc)
            if period is None:
                logger.info("No completed 14-day period to snapshot yet.")
                return {"statusCode": 200, "body": "No completed period to snapshot yet"}

            period_start, period_end = period
            logger.info(f"Leaderboard snapshot started. Period: {period_start} → {period_end}")

            results = aggregate_and_rank(session, period_start, period_end)
            logger.info(f"Aggregated {len(results)} climbers for this period")

            if not results:
                logger.warning("No verified climbs found for this period. No snapshot written.")
                return {"statusCode": 200, "body": "No climbs found, nothing to snapshot"}

            write_snapshots(session, results, period_start, period_end)
            session.commit()

            logger.info(f"Leaderboard reset complete. {len(results)} climbers ranked.")
            return {"statusCode": 200, "body": f"{len(results)} climbers ranked successfully"}

        except Exception as e:
            logger.error(f"Attempt {attempt} failed: {str(e)}")

            if session:
                session.rollback()

            if attempt < MAX_RETRIES:
                logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                logger.critical(
                    f"All {MAX_RETRIES} attempts failed. "
                    f"Leaderboard reset did NOT complete for period "
                    f"{period_start} → {period_end}. Manual intervention required."
                )
                raise

        finally:
            if session:
                session.close()
            if engine:
                engine.dispose()

if __name__ == "__main__":
    result = lambda_handler({}, {})
    print(result)