import pytest

from pydantic import ValidationError

from app.settings import Settings


@pytest.mark.parametrize("environment", ["dev", "test", "prod"])
def test_accepts_supported_environments(environment):
    settings = Settings(
        environment=environment,
        telegram_bot_token="42:ABC",
        airtable_access_token="token",
        _env_file=None,
    )

    assert settings.environment == environment


def test_rejects_partial_environment_matches():
    with pytest.raises(ValidationError):
        Settings(
            environment="production",
            telegram_bot_token="42:ABC",
            airtable_access_token="token",
            _env_file=None,
        )
