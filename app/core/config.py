from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    kobis_api_key: str | None = None

    # Scheduled collection batch (Step 7). Cron fires daily at HH:MM KST.
    scheduler_enabled: bool = True
    collection_cron_hour: int = 3
    collection_cron_minute: int = 0
    scheduler_timezone: str = "Asia/Seoul"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
