from fastapi import APIRouter

from app.api.v1.routes import ai, auth, health, tasks

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router)
api_router.include_router(tasks.router)
api_router.include_router(ai.router, prefix="/ai")
