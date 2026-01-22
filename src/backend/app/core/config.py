"""
Application configuration using Pydantic Settings.

Supports loading from:
- Environment variables (highest priority)
- .env file
- Default values

Compatible with Docker/Kubernetes deployments where
environment variables are injected at runtime.
"""

import os
from functools import lru_cache
from typing import List

from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with environment variable support.

    All settings can be overridden via environment variables.
    For example: PROJECT_NAME, DATABASE_URL, GROQ_API_KEY, etc.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,  # Allow both GROQ_API_KEY and groq_api_key
    )

    # Application Settings
    project_name: str = "Todo Webapp API"
    api_prefix: str = "/api"
    debug: bool = False  # Set DEBUG=true for detailed error messages

    # CORS Settings
    # Can be comma-separated list: "https://example.com,https://app.example.com"
    backend_cors_origins: str = "https://todo-web-app-red-mu.vercel.app,http://localhost:3000"

    # Database Settings
    database_url: str = os.getenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")

    # JWT/Auth Settings
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-me")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours

    # AI Provider Settings (Groq API)
    # IMPORTANT: Set GROQ_API_KEY in your environment for AI features
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    groq_base_url: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

    @property
    def parsed_cors_origins(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        if isinstance(self.backend_cors_origins, str):
            return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]
        return self.backend_cors_origins

    @property
    def is_ai_configured(self) -> bool:
        """Check if AI service is properly configured."""
        return bool(self.groq_api_key)

    @property
    def is_production_ready(self) -> bool:
        """Check if critical security settings are properly configured."""
        return (
            self.jwt_secret_key != "change-me" and
            "sqlite" not in self.database_url.lower()
        )


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Uses lru_cache to ensure settings are only loaded once.
    """
    return Settings()


settings = get_settings()
