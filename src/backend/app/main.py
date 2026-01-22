import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1.router import api_router
from app.db.base import init_db
from app.services.reminder_service import start_reminder_loop

# Configure logging for production debugging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_allowed_origins() -> List[str]:
    """
    Build the list of allowed CORS origins from environment and defaults.
    Supports Docker/Kubernetes environments via BACKEND_CORS_ORIGINS env var.
    """
    # Default origins that are always allowed
    default_origins = [
        "https://todo-web-app-red-mu.vercel.app",  # Production Vercel frontend
        "http://localhost:3000",                    # Local Next.js dev
        "http://localhost:8000",                    # Local backend (for docs)
        "http://127.0.0.1:3000",                   # Alternative localhost
    ]

    # Parse additional origins from environment variable
    env_origins = os.getenv("BACKEND_CORS_ORIGINS", "")
    if env_origins:
        additional = [origin.strip() for origin in env_origins.split(",") if origin.strip()]
        default_origins.extend(additional)

    # Remove duplicates while preserving order
    seen = set()
    unique_origins = []
    for origin in default_origins:
        if origin not in seen:
            seen.add(origin)
            unique_origins.append(origin)

    logger.info(f"CORS allowed origins: {unique_origins}")
    return unique_origins


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Initializes database tables on startup and starts background tasks.
    Validates critical environment variables.
    """
    # Startup: Validate environment
    logger.info("Starting Todo Backend API...")

    # Check critical environment variables
    if not os.getenv("GROQ_API_KEY") and not settings.groq_api_key:
        logger.warning("GROQ_API_KEY not set - AI features will be unavailable")
    else:
        logger.info("GROQ_API_KEY configured successfully")

    if settings.jwt_secret_key == "change-me":
        logger.warning("JWT_SECRET_KEY is using default value - please set in production")

    # Startup: Database initialize
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"CRITICAL: Database Init Error: {e}")

    # Start notification scheduler as a background task
    scheduler_task = asyncio.create_task(start_reminder_loop())
    logger.info("Reminder service started")

    yield

    # Shutdown: Cancel background tasks
    logger.info("Shutting down Todo Backend API...")
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

    # Global exception handler for unhandled errors
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal server error",
                "detail": str(exc) if os.getenv("DEBUG", "").lower() == "true" else "An unexpected error occurred"
            }
        )

    # Robust CORS Middleware Configuration
    # Explicitly define all allowed origins for production security
    allowed_origins = get_allowed_origins()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "Accept",
            "Origin",
            "X-Requested-With",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers",
        ],
        expose_headers=[
            "Content-Length",
            "X-Request-ID",
        ],
        max_age=600,  # Cache preflight requests for 10 minutes
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