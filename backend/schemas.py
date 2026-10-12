"""Pydantic data schemas for request and response validation."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class DocumentRequest(BaseModel):
    """Input payload for generating a legal document draft."""

    document_type: str = Field(
        ...,
        description="Type of legal document (e.g., Non-Disclosure Agreement, Employment Contract)",
        min_length=2,
        max_length=200,
        examples=["Non-Disclosure Agreement"],
    )
    parties: str = Field(
        ...,
        description="Names, roles, or entities involved in the agreement",
        min_length=2,
        max_length=2000,
        examples=["Alpha Corp (Disclosing Party), Beta LLC (Receiving Party)"],
    )
    terms: str = Field(
        ...,
        description="Core terms and conditions; semicolon or newline separated clauses",
        min_length=2,
        max_length=10000,
        examples=[
            "Confidentiality must be maintained for 2 years; Information used strictly for evaluation"
        ],
    )
    effective_date: str = Field(
        ...,
        description="Date when the agreement becomes legally effective",
        min_length=2,
        max_length=100,
        examples=["October 2, 2026"],
    )
    jurisdiction: Optional[str] = Field(
        default=None,
        description="Governing state, country, or jurisdiction (optional)",
        max_length=200,
        examples=["State of California, USA"],
    )
    additional_instructions: Optional[str] = Field(
        default=None,
        description="Special clauses, customized rules, or guidelines for the AI draft",
        max_length=3000,
        examples=["Include a dispute resolution clause with arbitration."],
    )

    @field_validator("document_type", "parties", "terms", "effective_date")
    @classmethod
    def check_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only")
        return v.strip()


class DocumentResponse(BaseModel):
    """Output payload containing generated legal document draft and metadata."""

    status: str = Field(default="success", description="Generation status code/message")
    document_type: str
    document_title: str
    content: str
    model_used: str
    source: str = Field(default="GEMINI", description="Generation source (GEMINI or FALLBACK)")
    notice: Optional[str] = Field(default=None, description="Informational notice regarding generator mode")
    effective_date: str
    disclaimer: str
    terms_list: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ExportRequest(BaseModel):
    """Payload for downloading or converting edited legal text into PDF, DOCX, or TXT."""

    document_title: str = Field(default="Legal Document", min_length=1)
    document_type: str = Field(default="Agreement", min_length=1)
    content: str = Field(..., min_length=1, description="Latest edited document content")
    effective_date: Optional[str] = None
    parties: Optional[str] = None
    terms: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check status response."""

    status: str = "healthy"
    app_name: str
    version: str
    gemini_configured: bool
    gemini_model: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
