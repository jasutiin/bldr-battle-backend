from fastapi import FastAPI

from auth.router import router as auth_router
from climbs.router import router as climbs_router
from leaderboard.router import router as leaderboard_router
from users.router import router as users_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(climbs_router)
app.include_router(leaderboard_router)