from pydantic import Field, HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Docs: https://docs.pydantic.dev/2.8/concepts/pydantic_settings/


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # `.env.prod` takes priority over `.env`
        env_file=(".env", ".env.prod"),
        env_file_encoding="utf-8",
    )

    # App name used in logs
    app_name: str = "algebrach"

    # Allows to detect type of deployment
    environment: str = Field(pattern=r"dev|test|prod")

    # Allows to detect environment
    is_docker: bool = False

    # Token got from https://t.me/BotFather
    telegram_bot_token: str

    # Access to Airtable storage: https://airtable.com/create/tokens
    airtable_access_token: str
    airtable_base_id: str = "appG5koP3D8kWbLdl"

    # Chat to forward runtime exceptions
    events_chat_id: int | None = None

    # URL to trigger every minute to detect app's crashes
    health_check_url: HttpUrl | None = None

    # Health check server configuration
    enable_health_check: bool = False
    health_check_port: int = 8080

    # --- Telegram Constants ---

    # System account IDs that should be ignored
    telegram_anonymous_admin_id: int = 1087968824
    telegram_channel_id: int = 777000

    # --- Cache Configuration ---

    # Cache TTL for Airtable queries (seconds)
    kek_cache_ttl_seconds: int = 300  # 5 minutes

    # --- Surprise Kek Configuration ---

    # Percentage chance of surprise kek triggering
    surprise_kek_chance_percent: int = 33

    # Maximum timeout in minutes for surprise kek punishment
    surprise_kek_max_timeout_minutes: int = 60

    # --- Admin Configuration ---

    # Admin user IDs (can be set via ADMIN_IDS env var as comma-separated values)
    admin_ids: str | set[int] = Field(
        default="28006241,207275675,217917985,126442350,221439208,147100358,258145124"
    )

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, v):
        """Parse admin IDs from comma-separated string or return set as-is."""
        if isinstance(v, str):
            return {int(x.strip()) for x in v.split(",") if x.strip()}
        return v

    mechmath_chat_id: int = -1001091546301
    rmbk_id: int = 28006241

    surprise_gif: str = "https://t.me/mechmath/743455"


config = Settings()
