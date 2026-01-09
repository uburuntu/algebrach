"""Tests for app/handlers/kek/kek_inline.py"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# Import from module directly (not via __init__.py to avoid router attachment issues)
from handlers.kek.kek_inline import (
    chosen_random_kek,
    get_text_keks,
    inline_kek_random,
    inline_kek_search,
    kek_to_result,
    search_keks,
)

# =============================================================================
# Helper function tests
# =============================================================================


class TestGetTextKeks:
    def test_filters_text_only_keks(self):
        keks = [
            {"id": "1", "fields": {"Text": "Text kek", "AttachmentType": None}},
            {"id": "2", "fields": {"Text": "Photo kek", "AttachmentType": "photo"}},
            {"id": "3", "fields": {"Text": "Another text", "AttachmentType": None}},
        ]

        result = get_text_keks(keks)

        assert len(result) == 2
        assert result[0]["id"] == "1"
        assert result[1]["id"] == "3"

    def test_filters_out_empty_text(self):
        keks = [
            {"id": "1", "fields": {"Text": "", "AttachmentType": None}},
            {"id": "2", "fields": {"Text": "Has text", "AttachmentType": None}},
            {"id": "3", "fields": {"AttachmentType": None}},  # No Text field
        ]

        result = get_text_keks(keks)

        assert len(result) == 1
        assert result[0]["id"] == "2"

    def test_empty_list(self):
        assert get_text_keks([]) == []


class TestSearchKeks:
    def test_finds_matching_keks(self):
        keks = [
            {"id": "1", "fields": {"Text": "Hello world"}},
            {"id": "2", "fields": {"Text": "Goodbye world"}},
            {"id": "3", "fields": {"Text": "Something else"}},
        ]

        result = search_keks(keks, "world")

        assert len(result) == 2
        assert result[0]["id"] == "1"
        assert result[1]["id"] == "2"

    def test_case_insensitive(self):
        keks = [
            {"id": "1", "fields": {"Text": "HELLO World"}},
            {"id": "2", "fields": {"Text": "hello world"}},
        ]

        result = search_keks(keks, "HELLO")

        assert len(result) == 2

    def test_no_matches(self):
        keks = [{"id": "1", "fields": {"Text": "Hello world"}}]

        result = search_keks(keks, "xyz")

        assert result == []

    def test_empty_keks(self):
        assert search_keks([], "query") == []

    def test_respects_limit(self):
        keks = [{"id": str(i), "fields": {"Text": f"kek {i}"}} for i in range(20)]

        result = search_keks(keks, "kek", limit=5)

        assert len(result) == 5


class TestKekToResult:
    def test_creates_article_with_kek_text(self):
        kek = {"id": "rec123", "fields": {"Text": "This is a kek"}}

        result = kek_to_result(kek)

        assert result.id == "rec123"
        assert result.title == "This is a kek"
        assert result.input_message_content.message_text == "This is a kek"

    def test_truncates_long_title(self):
        long_text = "A" * 100
        kek = {"id": "rec123", "fields": {"Text": long_text}}

        result = kek_to_result(kek)

        assert len(result.title) == 50
        assert result.description == "A" * 50  # Characters 50-100

    def test_no_description_for_short_text(self):
        kek = {"id": "rec123", "fields": {"Text": "Short"}}

        result = kek_to_result(kek)

        assert result.description is None


# =============================================================================
# Handler tests
# =============================================================================


def make_inline_query(query: str = "") -> MagicMock:
    """Create a mock InlineQuery."""
    mock = MagicMock()
    mock.query = query
    mock.answer = AsyncMock()
    return mock


def make_chosen_result(
    result_id: str = "test_id", inline_message_id: str | None = "msg_123"
) -> MagicMock:
    """Create a mock ChosenInlineResult."""
    mock = MagicMock()
    mock.result_id = result_id
    mock.inline_message_id = inline_message_id
    mock.from_user = MagicMock()
    mock.from_user.id = 123
    return mock


class TestInlineKekRandom:
    @pytest.mark.asyncio
    async def test_returns_single_random_option(self):
        query = make_inline_query("")

        await inline_kek_random(query)

        query.answer.assert_awaited_once()
        results = query.answer.call_args.args[0]
        assert len(results) == 1
        assert results[0].title == "🎲 Случайный кек"

    @pytest.mark.asyncio
    async def test_uses_correct_cache_settings(self):
        query = make_inline_query("")

        await inline_kek_random(query)

        call_kwargs = query.answer.call_args.kwargs
        assert call_kwargs["cache_time"] == 5 * 60
        assert call_kwargs["is_personal"] is False


class TestInlineKekSearch:
    @pytest.fixture
    def mock_storage(self):
        storage = MagicMock()
        storage.async_all = AsyncMock(
            return_value=[
                {"id": "1", "fields": {"Text": "Hello world", "AttachmentType": None}},
                {
                    "id": "2",
                    "fields": {"Text": "Goodbye world", "AttachmentType": None},
                },
                {"id": "3", "fields": {"Text": "Photo kek", "AttachmentType": "photo"}},
            ]
        )
        return storage

    @pytest.mark.asyncio
    async def test_returns_matching_keks(self, mock_storage):
        query = make_inline_query("world")

        with patch("handlers.kek.kek_inline.kek_storage", mock_storage):
            await inline_kek_search(query)

        query.answer.assert_awaited_once()
        results = query.answer.call_args.args[0]
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_returns_not_found_for_no_matches(self, mock_storage):
        query = make_inline_query("xyz123")

        with patch("handlers.kek.kek_inline.kek_storage", mock_storage):
            await inline_kek_search(query)

        query.answer.assert_awaited_once()
        results = query.answer.call_args.args[0]
        assert len(results) == 1
        assert results[0].id == "not_found"
        assert "не найдено" in results[0].title

    @pytest.mark.asyncio
    async def test_limits_to_10_results(self, mock_storage):
        # Create 15 matching keks
        mock_storage.async_all = AsyncMock(
            return_value=[
                {"id": str(i), "fields": {"Text": f"Kek {i}", "AttachmentType": None}}
                for i in range(15)
            ]
        )
        query = make_inline_query("Kek")

        with patch("handlers.kek.kek_inline.kek_storage", mock_storage):
            await inline_kek_search(query)

        results = query.answer.call_args.args[0]
        assert len(results) == 10


class TestChosenRandomKek:
    @pytest.fixture
    def mock_storage(self):
        storage = MagicMock()
        storage.async_all = AsyncMock(
            return_value=[
                {"id": "rec1", "fields": {"Text": "First kek", "AttachmentType": None}},
                {
                    "id": "rec2",
                    "fields": {"Text": "Second kek", "AttachmentType": None},
                },
            ]
        )
        return storage

    @pytest.fixture
    def mock_bot(self):
        bot = MagicMock()
        bot.edit_message_text = AsyncMock()
        return bot

    @pytest.mark.asyncio
    async def test_edits_message_with_random_kek(self, mock_storage, mock_bot):
        chosen = make_chosen_result(result_id="random_uuid")

        with patch("handlers.kek.kek_inline.kek_storage", mock_storage):
            await chosen_random_kek(chosen, mock_bot)

        mock_bot.edit_message_text.assert_awaited_once()
        call_kwargs = mock_bot.edit_message_text.call_args.kwargs
        assert call_kwargs["text"] in ["First kek", "Second kek"]
        assert call_kwargs["inline_message_id"] == "msg_123"

    @pytest.mark.asyncio
    async def test_handles_empty_storage(self, mock_bot):
        empty_storage = MagicMock()
        empty_storage.async_all = AsyncMock(return_value=[])
        chosen = make_chosen_result(result_id="any_id")

        with patch("handlers.kek.kek_inline.kek_storage", empty_storage):
            await chosen_random_kek(chosen, mock_bot)

        mock_bot.edit_message_text.assert_awaited_once()
        call_kwargs = mock_bot.edit_message_text.call_args.kwargs
        assert "нет" in call_kwargs["text"]

    @pytest.mark.asyncio
    async def test_skips_if_no_inline_message_id(self, mock_storage, mock_bot):
        chosen = make_chosen_result(result_id="rec1", inline_message_id=None)

        with patch("handlers.kek.kek_inline.kek_storage", mock_storage):
            await chosen_random_kek(chosen, mock_bot)

        mock_bot.edit_message_text.assert_not_awaited()
