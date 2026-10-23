from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Uzbek Reform Transliteration API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "*"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"

    # Telegram Web App
    TELEGRAM_BOT_TOKEN: str = ""
    INIT_DATA_MAX_AGE_SECONDS: int = 86400  # 24 hours validity

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
