import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Multilingual Conversational Dashboard System"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    SESSION_TTL_MINUTES: int = 60
    MAX_UPLOAD_SIZE_MB: int = 50
    WHISPER_MODEL_SIZE: str = "base"  # configurable: tiny, base, small
    CORS_ORIGINS: list = ["*"]

    class Config:
        env_file = ".env"

settings = Settings()