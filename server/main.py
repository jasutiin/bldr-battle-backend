from fastapi import FastAPI
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

from routers import users, climbs, comments, admin

app = FastAPI()

app.include_router(users.router)
app.include_router(climbs.router)
app.include_router(comments.router)
app.include_router(admin.router)