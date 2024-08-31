import pytest
from unittest.mock import Mock, patch
from aiogram.types import User
from app.airtable.kek_storage import KekStorage


@pytest.fixture
def kek_storage():
    return KekStorage()


@pytest.mark.asyncio
async def test_async_all(kek_storage):
    mock_all = Mock(return_value=[{"id": 1, "fields": {"Text": "Test kek"}}])
    kek_storage.all = mock_all

    result = await kek_storage.async_all()

    assert result == [{"id": 1, "fields": {"Text": "Test kek"}}]
    mock_all.assert_called_once()


@pytest.mark.asyncio
async def test_async_add(kek_storage):
    mock_add = Mock(return_value={"id": 1, "fields": {"Text": "New kek"}})
    kek_storage.add = mock_add

    author = User(id=1, is_bot=False, first_name="Test")
    suggestor = User(id=2, is_bot=False, first_name="Suggestor")

    result = await kek_storage.async_add(
        author=author,
        suggestor=suggestor,
        text="New kek",
        attachment_url=None,
        attachment_type=None,
        attachment_filename=None,
        attachment_file_id=None,
    )

    assert result == {"id": 1, "fields": {"Text": "New kek"}}
    mock_add.assert_called_once_with(
        author, suggestor, "New kek", None, None, None, None
    )


@pytest.mark.asyncio
async def test_async_push(kek_storage):
    mock_push = Mock(return_value={"id": 1, "fields": {"Text": "Pushed kek"}})
    kek_storage.push = mock_push

    author = User(id=1, is_bot=False, first_name="Test")

    result = await kek_storage.async_push(
        author=author,
        text="Pushed kek",
        attachment_url=None,
        attachment_type=None,
        attachment_filename=None,
        attachment_file_id=None,
    )

    assert result == {"id": 1, "fields": {"Text": "Pushed kek"}}
    mock_push.assert_called_once_with(author, "Pushed kek", None, None, None, None)
