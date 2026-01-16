import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router
from app.db.base import init_db
from app.services.reminder_service import start_reminder_loop

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Initializes database tables on startup and starts background tasks.
    """
    # Startup: Database initialize
    try:
        init_db()
    except Exception as e:
        print(f"CRITICAL: Database Init Error: {e}")

    # Start notification scheduler as a background task
    scheduler_task = asyncio.create_task(start_reminder_loop())

    yield

    # Shutdown: Cancel background tasks
    scheduler_task.cancel()
    try:
        await scheduler_task
    except asyncio.CancelledError:
        pass

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.project_name,
        openapi_url=f"{settings.api_prefix}/openapi.json",
        docs_url=f"{settings.api_prefix}/docs",
        redoc_url=f"{settings.api_prefix}/redoc",
        lifespan=lifespan,
    )

    # CORS UPDATED: Specific domains + Wildcard for local testing
    # Railway aur Vercel ke darmiyan "Failed to fetch" isi se hal hoga
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://todo-web-app-red-mu.vercel.app", # Aapka asali frontend
            "http://localhost:3000",                  # Local testing
            "*"                                       # Safe fallback
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"], # Taake headers frontend ko mil saken
    )

    # Root endpoint
    @app.get("/", include_in_schema=False)
    def root():
        return {
            "message": "Todo API is running",
            "docs": f"{settings.api_prefix}/docs",
            "redoc": f"{settings.api_prefix}/redoc"
        }

    # HEALTH CHECK: Railway automation ke liye zaroori rasta
    @app.get("/api/health", tags=["health"])
    def health_check():
        return {"status": "healthy", "service": "todo-backend", "environment": os.environ.get("RAILWAY_ENVIRONMENT", "local")}

    # Include API router
    app.include_router(api_router, prefix=settings.api_prefix)

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    # Railway defaults to port 8080 or dynamic PORT
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)