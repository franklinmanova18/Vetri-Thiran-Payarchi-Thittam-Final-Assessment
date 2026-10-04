from typing import Optional

from pydantic import BaseModel, Field, field_validator


class DocumentRequest(BaseModel):

    document_type: str = Field(
        default="General Agreement",
        max_length=120
    )

    parties: str = Field(
        default="",
        max_length=4000
    )

    terms: str = Field(
        default="",
        max_length=12000
    )

    effective_date: str = Field(
        default="",
        max_length=100
    )

    jurisdiction: str = Field(
        default="",
        max_length=200
    )

    additional_instructions: str = Field(
        default="",
        max_length=5000
    )

    include_disclaimer: bool = True

    logo_base64: Optional[str] = None

    @field_validator(
        "document_type",
        "parties",
        "terms",
        "effective_date"
    )
    @classmethod
    def clean_text(cls, value):

        if value is None:
            return ""

        return str(value).strip()

    @field_validator("logo_base64")
    @classmethod
    def validate_logo(cls, value):

        if value and len(value) > 4_000_000:
            raise ValueError(
                "Logo file is too large."
            )

        return value


class DocumentResponse(BaseModel):

    document_type: str
    content: str
    model: str
    demo_mode: bool