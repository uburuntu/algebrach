from pydantic import Field, HttpUrl
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

    # --- Non essentials ---

    admin_ids: set[int] = Field(
        default_factory=lambda: [
            28006241,
            207275675,
            217917985,
            126442350,
            221439208,
            147100358,
            258145124,
        ]
    )

    mechmath_chat_id: int = -1001091546301
    rmbk_id: int = 28006241

    surprise_gif: str = "https://t.me/mechmath/743455"


config = Settings()
