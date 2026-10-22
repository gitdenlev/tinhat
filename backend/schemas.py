"""Pydantic request models."""

import re

from pydantic import BaseModel, Field, field_validator

from .config import (
    DEFAULT_LIFETIME,
    E2EE_PREFIX,
    MAX_ENCRYPTED_PAYLOAD_LENGTH,
    MAX_LIFETIME,
    MAX_SECRET_LENGTH,
    MIN_LIFETIME,
)

_E2EE_FORMAT_RE = re.compile(r"^e2ee:v1:[A-Za-z0-9_-]{16}\.[A-Za-z0-9_-]{22,}$")


class CreateSecretRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=MAX_ENCRYPTED_PAYLOAD_LENGTH,
        description="Confidential secret text message (or client-encrypted e2ee:v1 payload)",
    )
    lifetime: int = Field(default=DEFAULT_LIFETIME, ge=MIN_LIFETIME, le=MAX_LIFETIME)

    @field_validator("text")
    @classmethod
    def validate_secret_text(cls, value: str) -> str:
        if value.startswith(E2EE_PREFIX):
            if len(value) > MAX_ENCRYPTED_PAYLOAD_LENGTH or not _E2EE_FORMAT_RE.match(value):
                raise ValueError("Invalid encrypted secret payload format or length.")
            return value
        if len(value) > MAX_SECRET_LENGTH:
            raise ValueError(
                f"String should have at most {MAX_SECRET_LENGTH} characters"
            )
        return value
