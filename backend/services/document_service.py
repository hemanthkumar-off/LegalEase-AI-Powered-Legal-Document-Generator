"""Document generation and orchestration service for LegalEase."""

import logging
from typing import Dict, Any, List

from backend.config import settings
from backend.schemas import DocumentRequest, DocumentResponse
from backend.ai_core.gemini_generator import GeminiDocumentGenerator
from backend.utils.text_utils import sanitize_text, parse_terms

logger = logging.getLogger("LegalEase.DocumentService")


class DocumentService:
    """Service handling legal document creation and formatting pipeline."""

    def __init__(self, generator: GeminiDocumentGenerator = None):
        self.generator = generator or GeminiDocumentGenerator()

    def generate_draft(self, request: DocumentRequest) -> DocumentResponse:
        """Process document request, generate AI draft via Gemini, and package response."""
        # Sanitize incoming fields
        clean_request = DocumentRequest(
            document_type=sanitize_text(request.document_type),
            parties=sanitize_text(request.parties),
            terms=sanitize_text(request.terms),
            effective_date=sanitize_text(request.effective_date),
            jurisdiction=sanitize_text(request.jurisdiction) if request.jurisdiction else None,
            additional_instructions=(
                sanitize_text(request.additional_instructions)
                if request.additional_instructions
                else None
            ),
        )

        # Call AI generator
        ai_result = self.generator.generate_document(clean_request)

        # Extract parsed terms
        terms_list = parse_terms(clean_request.terms)

        return DocumentResponse(
            status="success",
            document_type=clean_request.document_type,
            document_title=ai_result.get("document_title", clean_request.document_type),
            content=ai_result.get("content", ""),
            model_used=ai_result.get("model_used", settings.GEMINI_MODEL),
            source=ai_result.get("source", "GEMINI"),
            notice=ai_result.get("notice"),
            effective_date=clean_request.effective_date,
            disclaimer=settings.LEGAL_DISCLAIMER,
            terms_list=terms_list,
        )
