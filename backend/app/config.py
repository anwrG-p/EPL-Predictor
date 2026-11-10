from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./data/backend.db"
    MODEL_TYPE: str = "ensemble"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False
        env_prefix = ""

settings = Settings()
