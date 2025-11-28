from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "Portfolio API"
    ENV: str = "development"
    DATABASE_URL: str = "sqlite+aiosqlite:///./portfolio.db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "portfolio_db"
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    ALLOW_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]
    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1", "*"]

    class Config:
        env_file = ".env"


settings = Settings()
