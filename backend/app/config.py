import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "default_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = "sqlite:///./data/backend.db"
    ADMIN_EMAIL: str = "admin@email.com"
    MODEL_TYPE: str = "ensemble"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False
        # Allow environment variables to override .env file
        env_prefix = ""

settings = Settings()
