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


def test_uses_safe_polling_defaults():
    settings = Settings(
        environment="test",
        telegram_bot_token="42:ABC",
        airtable_access_token="token",
        _env_file=None,
    )

    assert settings.drop_pending_updates is False
    assert settings.polling_tasks_concurrency_limit == 32


def test_rejects_non_positive_polling_limit():
    with pytest.raises(ValidationError):
        Settings(
            environment="test",
            telegram_bot_token="42:ABC",
            airtable_access_token="token",
            polling_tasks_concurrency_limit=0,
            _env_file=None,
        )
