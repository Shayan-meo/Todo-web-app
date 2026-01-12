import os
from functools import lru_cache
from typing import List

from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    project_name: str = "Todo Webapp API"
    api_prefix: str = "/api"

    backend_cors_origins: str = "*"  # Allow all origins by default for production ease

    database_url: str = os.getenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours

    # AI Provider Settings (Groq API)
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    groq_base_url: str = "https://api.groq.com/openai/v1"

    @property
    def parsed_cors_origins(self) -> List[str]:
        if isinstance(self.backend_cors_origins, str):
            return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]
        return self.backend_cors_origins


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
