from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BACK_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    APP_NAME: str = "Uzbek Reform Transliteration API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "*"

    # Database: default to app.db inside back directory
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BACK_DIR / 'app.db'}"

    @property
    def async_database_url(self) -> str:
        """
        Ensures the database URL is compatible with SQLAlchemy's async engine.
        Render and many cloud providers provide PostgreSQL URLs starting with
        'postgres://' or 'postgresql://'. This normalizes them to 'postgresql+asyncpg://'.
        """
        url = self.DATABASE_URL.strip()
        if url.startswith("sqlite+aiosqlite:///./"):
            # Resolve relative SQLite URL relative to back/ directory
            rel_path = url[len("sqlite+aiosqlite:///./"):]
            return f"sqlite+aiosqlite:///{BACK_DIR / rel_path}"
        elif url.startswith("sqlite:///./"):
            rel_path = url[len("sqlite:///./"):]
            return f"sqlite+aiosqlite:///{BACK_DIR / rel_path}"
        elif url.startswith("postgres://"):
            return "postgresql+asyncpg://" + url[len("postgres://"):]
        elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
            return "postgresql+asyncpg://" + url[len("postgresql://"):]
        return url

    # Telegram Web App
    TELEGRAM_BOT_TOKEN: str = ""
    INIT_DATA_MAX_AGE_SECONDS: int = 86400  # 24 hours validity
    NODE_ENV: str = ""

    @property
    def is_development(self) -> bool:
        env = (self.NODE_ENV or self.APP_ENV).lower()
        return env in ("development", "dev", "local", "test")

    model_config = SettingsConfigDict(
        env_file=BACK_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
