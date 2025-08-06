from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения, считываемые из .env или переменных окружения."""

    # ─── база данных ────────────────────────────────
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DB_ECHO: bool = Field(False, alias="DB_ECHO")

    # ─── JWT ────────────────────────────────────────
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_EXPIRE_MIN: int = Field(5, env="ACCESS_EXPIRE_MIN")
    REFRESH_EXPIRE_DAYS: int = Field(30, env="REFRESH_EXPIRE_DAYS")

    # ─── прочее ─────────────────────────────────────
    ENV: str = Field("dev", env="ENV")
    DEBUG: bool = Field(True, env="DEBUG")

    # ↓↓↓ всё, что раньше было в class Config ↓↓↓
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",          # незнакомые переменные окружения игнорируем
        case_sensitive=False,    # DATABASE_URL и database_url эквивалентны
    )


settings = Settings()
