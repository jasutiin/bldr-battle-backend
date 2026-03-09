from fastapi import FastAPI

from admin.router import router as admin_router
from climbs.router import router as climbs_router
from comments.router import router as comments_router
from users.router import router as users_router

app = FastAPI()

app.include_router(users_router)
app.include_router(climbs_router)
app.include_router(comments_router)
app.include_router(admin_router)