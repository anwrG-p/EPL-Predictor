from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "default_secret_key_change_in_production"
    FASTAPI_SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    JWT_ALGORITHM: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = "sqlite:///./data/backend.db"
    ADMIN_EMAIL: str = "admin@email.com"
    MODEL_TYPE: str = "ensemble"

    def model_post_init(self, __context):
        if self.FASTAPI_SECRET_KEY and self.SECRET_KEY == "default_secret_key_change_in_production":
            self.SECRET_KEY = self.FASTAPI_SECRET_KEY
        if self.JWT_ALGORITHM:
            self.ALGORITHM = self.JWT_ALGORITHM

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False
        env_prefix = ""

settings = Settings()
