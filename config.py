from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Uzbek Reform Transliteration API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "*"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"

    @property
    def async_database_url(self) -> str:
        """
        Ensures the database URL is compatible with SQLAlchemy's async engine.
        Render and many cloud providers provide PostgreSQL URLs starting with
        'postgres://' or 'postgresql://'. This normalizes them to 'postgresql+asyncpg://'.
        """
        url = self.DATABASE_URL.strip()
        if url.startswith("postgres://"):
            return "postgresql+asyncpg://" + url[len("postgres://"):]
        elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
            return "postgresql+asyncpg://" + url[len("postgresql://"):]
        return url

    # Telegram Web App
    TELEGRAM_BOT_TOKEN: str = ""
    INIT_DATA_MAX_AGE_SECONDS: int = 86400  # 24 hours validity

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
