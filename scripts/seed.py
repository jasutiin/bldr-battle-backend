import os
from datetime import datetime, timedelta
from supabase import create_client
import random
import uuid
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

GRADES = ["A", "B", "C", "D"]
GRADE_POINTS = {
    "A": 100,
    "B": 200,
    "C": 400,
    "D": 800
}

CLIMB_NAMES = [
    "The Crimper Problem",
    "Slopey Boi",
    "Dynamo",
    "The Overhang",
    "Pinch King",
    "The Traverse",
    "Heel Hook Heaven",
    "The Mantle",
    "Roof Runner",
    "Pocket Rocket"
]

def calculate_points(grade: str, climb_date: datetime, period_start: datetime) -> int:
    base_points = GRADE_POINTS[grade]
    days_elapsed = (climb_date - period_start).days
    decay_multiplier = max(0.60, 1 - (days_elapsed * 0.03))
    return round(base_points * decay_multiplier)

def seed_users(num_users=10):
    print(f"Seeding {num_users} users...")
    users = []

    for i in range(num_users):
        email = f"climber{i+1}@boulderbattle.com"
        password = "password123"

        auth_response = supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,
            "app_metadata": {"role": "admin"} if i == 0 else {}  # first user is admin
        })

        user_id = auth_response.user.id

        supabase.table("users").insert({
            "id": user_id,
            "username": f"climber{i+1}"
        }).execute()

        users.append({"id": user_id, "username": f"climber{i+1}"})
        role = "admin" if i == 0 else "climber"
        print(f"  Created {role}: climber{i+1} ({user_id})")

    return users

def seed_climbs(users, num_climbs_per_user=5):
    print(f"Seeding climbs for {len(users)} users...")

    period_start = datetime.utcnow() - timedelta(days=14)

    for user in users:
        for _ in range(num_climbs_per_user):
            grade = random.choice(GRADES)

            # random day within the current period
            days_offset = random.randint(0, 13)
            climb_date = period_start + timedelta(days=days_offset)

            points = calculate_points(grade, climb_date, period_start)

            supabase.table("climbs").insert({
                "id": str(uuid.uuid4()),
                "user_id": user["id"],
                "grade": grade,
                "name": random.choice(CLIMB_NAMES),
                "video_url": f"videos/{uuid.uuid4()}.mp4",
                "verified": True,           # pre-verify so Lambda can count them
                "points": points,
                "created_at": climb_date.isoformat(),
                "effective_date": climb_date.isoformat()
            }).execute()

        print(f"  Seeded {num_climbs_per_user} climbs for {user['username']}")

if __name__ == "__main__":
    users = seed_users(num_users=10)
    seed_climbs(users, num_climbs_per_user=5)
    print("Seeding complete.")