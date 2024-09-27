from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Project settings loaded from .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    APP_NAME: str
    APP_HOST: str
    APP_PORT: int
    APP_WORKERS: int

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: str
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_ECHO: int

    SCHEDULE_FOR_DAYS: int

    def get_database_uri(self) -> str:
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}"
            f"/{self.POSTGRES_DB}"
        )


settings = Settings()
