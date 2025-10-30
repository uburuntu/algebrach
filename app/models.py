"""Pydantic models for data validation."""

from pydantic import BaseModel, Field


class AirtableAttachment(BaseModel):
    """Airtable attachment field structure."""

    url: str
    filename: str | None = None
    id: str | None = None
    size: int | None = None
    type: str | None = None


class KekFields(BaseModel):
    """Fields structure for a Kek record."""

    Text: str | None = None
    AttachmentType: str | None = None
    AttachmentFileID: str | None = None
    Attachment: list[AirtableAttachment] | None = None
    Author: list[str] = Field(default_factory=list)  # Airtable record IDs
    Suggestor: list[str] | None = None


class KekRecord(BaseModel):
    """Complete Kek record from Airtable."""

    id: str
    fields: KekFields
    createdTime: str | None = None


class UserFields(BaseModel):
    """Fields structure for a User record."""

    TelegramID: int
    Name: str
    Username: str | None = None
    LanguageCode: str | None = None
    AuthoredKeks: int | None = None
    SuggestedKeks: int | None = None


class UserRecord(BaseModel):
    """Complete User record from Airtable."""

    id: str
    fields: UserFields
    createdTime: str | None = None
