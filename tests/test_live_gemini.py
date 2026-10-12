"""Optional live Gemini API test.

This test is skipped by default to avoid quota consumption during automated CI runs.
To execute this test, run:
pytest tests/test_live_gemini.py -v -s -m live
or set RUN_LIVE_GEMINI_TEST=1 in the environment.
"""

import os
import pytest

from backend.config import settings
from backend.ai_core.gemini_generator import GeminiDocumentGenerator
from backend.schemas import DocumentRequest


RUN_LIVE = os.getenv("RUN_LIVE_GEMINI_TEST", "0") == "1"
HAS_KEY = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip() and not settings.GEMINI_API_KEY.startswith("AQ."))


@pytest.mark.skipif(
    not (RUN_LIVE and HAS_KEY),
    reason="Live Gemini test skipped. Enable with RUN_LIVE_GEMINI_TEST=1 and a valid AI Studio API key.",
)
def test_live_gemini_nda_generation():
    """Live verification test against real Google Gemini API."""
    gen = GeminiDocumentGenerator()
    req = DocumentRequest(
        document_type="Non-Disclosure Agreement",
        parties="Alpha Technologies (Disclosing Party), Beta Solutions (Receiving Party)",
        terms=(
            "Confidential information must not be shared; "
            "Information may only be used for project evaluation; "
            "Confidentiality period is 2 years"
        ),
        effective_date="October 2, 2026",
        jurisdiction="State of California, USA",
        additional_instructions="Include an injunctive relief clause.",
    )

    result = gen.generate_document(req)
    assert result is not None
    assert "content" in result
    assert len(result["content"]) > 100
    assert result["source"] == "GEMINI"
    assert "Alpha Technologies" in result["content"] or "Disclosing Party" in result["content"]
