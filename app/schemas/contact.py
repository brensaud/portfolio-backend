"""
Pydantic schemas for the contact API.

ContactMessageCreate  — request body for POST /api/v1/contact/messages
ContactMessageResponse — 201 Created response body
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class ContactMessageCreate(BaseModel):
    """Validated request body for a new contact message."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Sender's full name",
        examples=["Jane Smith"],
    )
    email: EmailStr = Field(
        ...,
        description="Sender's email address",
        examples=["jane@example.com"],
    )
    subject: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Message subject",
        examples=["Hiring inquiry"],
    )
    message: str = Field(
        ...,
        min_length=20,
        max_length=5000,
        description="Message body (min 20 characters)",
        examples=["Hello, I'd like to discuss a backend engineering opportunity."],
    )

    @field_validator("name", "subject", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()

    @field_validator("message", mode="before")
    @classmethod
    def strip_message(cls, v: str) -> str:
        return v.strip()


class ContactMessageResponse(BaseModel):
    """Response body returned after a successful submission."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    message: str
    reference_id: str
