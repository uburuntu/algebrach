"""Tests for Pydantic models."""

import pytest

from pydantic import ValidationError

from models import AirtableAttachment, KekFields, KekRecord, UserFields, UserRecord


def test_airtable_attachment_valid():
    """Test valid AirtableAttachment creation."""
    attachment = AirtableAttachment(
        url="https://example.com/file.jpg",
        filename="file.jpg",
        id="att123",
        size=1024,
        type="image/jpeg",
    )

    assert attachment.url == "https://example.com/file.jpg"
    assert attachment.filename == "file.jpg"
    assert attachment.id == "att123"
    assert attachment.size == 1024
    assert attachment.type == "image/jpeg"


def test_airtable_attachment_minimal():
    """Test AirtableAttachment with only required fields."""
    attachment = AirtableAttachment(url="https://example.com/file.jpg")

    assert attachment.url == "https://example.com/file.jpg"
    assert attachment.filename is None
    assert attachment.id is None
    assert attachment.size is None
    assert attachment.type is None


def test_kek_fields_valid():
    """Test valid KekFields creation."""
    fields = KekFields(
        Text="Test kek",
        AttachmentType="photo",
        AttachmentFileID="AgACAgIAAxkBAAI...",
        Attachment=[
            AirtableAttachment(url="https://example.com/photo.jpg", filename="photo.jpg")
        ],
        Author=["recAuthor123"],
        Suggestor=["recSuggestor456"],
    )

    assert fields.Text == "Test kek"
    assert fields.AttachmentType == "photo"
    assert fields.AttachmentFileID == "AgACAgIAAxkBAAI..."
    assert len(fields.Attachment) == 1
    assert fields.Author == ["recAuthor123"]
    assert fields.Suggestor == ["recSuggestor456"]


def test_kek_fields_minimal():
    """Test KekFields with minimal data."""
    fields = KekFields()

    assert fields.Text is None
    assert fields.AttachmentType is None
    assert fields.AttachmentFileID is None
    assert fields.Attachment is None
    assert fields.Author == []
    assert fields.Suggestor is None


def test_kek_record_valid():
    """Test valid KekRecord creation."""
    record = KekRecord(
        id="rec123",
        fields=KekFields(Text="Test kek", Author=["recAuthor123"]),
        createdTime="2024-01-01T00:00:00.000Z",
    )

    assert record.id == "rec123"
    assert record.fields.Text == "Test kek"
    assert record.createdTime == "2024-01-01T00:00:00.000Z"


def test_kek_record_missing_id():
    """Test that KekRecord requires id field."""
    with pytest.raises(ValidationError):
        KekRecord(fields=KekFields(Text="Test kek"))


def test_user_fields_valid():
    """Test valid UserFields creation."""
    fields = UserFields(
        TelegramID=123456,
        Name="John Doe",
        Username="johndoe",
        LanguageCode="en",
        AuthoredKeks=10,
        SuggestedKeks=5,
    )

    assert fields.TelegramID == 123456
    assert fields.Name == "John Doe"
    assert fields.Username == "johndoe"
    assert fields.LanguageCode == "en"
    assert fields.AuthoredKeks == 10
    assert fields.SuggestedKeks == 5


def test_user_fields_minimal():
    """Test UserFields with only required fields."""
    fields = UserFields(TelegramID=123456, Name="John Doe")

    assert fields.TelegramID == 123456
    assert fields.Name == "John Doe"
    assert fields.Username is None
    assert fields.LanguageCode is None
    assert fields.AuthoredKeks is None
    assert fields.SuggestedKeks is None


def test_user_record_valid():
    """Test valid UserRecord creation."""
    record = UserRecord(
        id="recUser123",
        fields=UserFields(TelegramID=123456, Name="John Doe"),
        createdTime="2024-01-01T00:00:00.000Z",
    )

    assert record.id == "recUser123"
    assert record.fields.TelegramID == 123456
    assert record.fields.Name == "John Doe"


def test_user_record_missing_telegram_id():
    """Test that UserFields requires TelegramID."""
    with pytest.raises(ValidationError):
        UserFields(Name="John Doe")
