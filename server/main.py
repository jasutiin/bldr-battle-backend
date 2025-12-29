from fastapi import FastAPI

from routers import users, climbs, comments

app = FastAPI()

app.include_router(users.router)
app.include_router(climbs.router)
app.include_router(comments.router)