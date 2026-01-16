import asyncio
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
    Initializes database tables on startup.
    Starts background tasks.
    """
    # Startup: Database initialize karein
    try:
        init_db()
    except Exception as e:
        print(f"Database Init Error: {e}")

    # Start notification scheduler
    scheduler_task = asyncio.create_task(start_reminder_loop())

    yield

    # Shutdown
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

    # CORS FIXED: Sab origins allow kar diye taake Vercel block na ho
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Root endpoint
    @app.get("/", include_in_schema=False)
    def root():
        return {
            "message": "Todo API is running",
            "docs": "/api/docs",
            "redoc": "/api/redoc"
        }

    # HEALTH CHECK ADDED: Railway is raste se check karega ke app sahi chal rahi hai
    @app.get("/api/health")
    def health_check():
        return {"status": "healthy", "service": "todo-backend"}

    # Include API router
    app.include_router(api_router, prefix=settings.api_prefix)

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    import os
    # Railway aksar PORT environment variable deta hai, hum usay use karenge
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)