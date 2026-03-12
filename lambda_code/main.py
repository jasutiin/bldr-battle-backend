import os
import boto3
import logging
import time
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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

def aggregate_and_rank(session, period_start, period_end):
    result = session.execute(text("""
        SELECT user_id, SUM(points) as total_points, COUNT(*) as climb_count
        FROM climbs
        WHERE verified = true
        AND effective_date BETWEEN :start AND :end
        GROUP BY user_id
        ORDER BY total_points DESC
        LIMIT 100
    """), {"start": period_start, "end": period_end})
    return result.fetchall()

def write_snapshots(session, results, period_start, period_end):
    rows = [
        {
            "user_id": str(row.user_id),
            "period_start": period_start,
            "period_end": period_end,
            "total_points": row.total_points,
            "climb_count": row.climb_count,
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

    period_end = datetime.utcnow()
    period_start = period_end - timedelta(days=14)

    logger.info(f"Leaderboard reset started. Period: {period_start} → {period_end}")

    session = None
    engine = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            session, engine = get_db_session()

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