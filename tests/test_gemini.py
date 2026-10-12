"""Tests for Gemini AI Core integration, prompt engineering, and error handling."""

import pytest
from unittest.mock import MagicMock, patch

from backend.ai_core.gemini_generator import GeminiDocumentGenerator, GeminiServiceError
from backend.schemas import DocumentRequest


def test_system_instruction_contains_anti_hallucination_rules():
    """Verify system instruction explicitly bans hallucinating facts and mandates placeholders."""
    gen = GeminiDocumentGenerator(api_key="mock_key")
    sys_inst = gen.build_system_instruction()

    assert "NO FACTUAL HALLUCINATIONS" in sys_inst
    assert "CLEAR BRACKETED PLACEHOLDERS" in sys_inst
    assert "ADAPTIVE STRUCTURE" in sys_inst
    assert "LEGAL DISCLAIMER" in sys_inst


def test_build_prompt_incorporates_all_user_inputs(sample_nda_request):
    """Verify prompt incorporates document type, parties, terms, date, and jurisdiction."""
    gen = GeminiDocumentGenerator(api_key="mock_key")
    req = DocumentRequest(**sample_nda_request)
    prompt = gen.build_prompt(req)

    assert "Non-Disclosure Agreement" in prompt
    assert "Alpha Technologies" in prompt
    assert "Beta Solutions" in prompt
    assert "October 2, 2026" in prompt
    assert "State of California, USA" in prompt
    assert "injunctive relief" in prompt


def test_generate_document_missing_api_key_activates_fallback():
    """Verify generator cleanly falls back to built-in engine when API key is missing or invalid."""
    gen = GeminiDocumentGenerator(api_key="")
    req = DocumentRequest(
        document_type="Non-Disclosure Agreement",
        parties="Party Alpha and Party Beta",
        terms="Term 1: Confidentiality for 2 years; Term 2: Return of materials",
        effective_date="October 2, 2026",
    )
    result = gen.generate_document(req)
    assert result is not None
    assert result["source"] == "FALLBACK"
    assert "NON-DISCLOSURE AGREEMENT" in result["document_title"]
    assert "Party Alpha" in result["content"]
    assert "Confidentiality for 2 years" in result["content"]
    assert "notice" in result


def test_get_client_missing_key_raises_error():
    """Verify _get_client explicitly raises GeminiServiceError when key is blank."""
    gen = GeminiDocumentGenerator(api_key="")
    with pytest.raises(GeminiServiceError) as exc_info:
        gen._get_client()
    assert exc_info.value.status_code == 401


def test_generate_document_successful_mock():
    """Verify generator properly parses response and returns metadata."""
    gen = GeminiDocumentGenerator(api_key="dummy_valid_format_key")

    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.text = "# EMPLOYMENT CONTRACT\n\nThis is a mocked contract agreement text."
    mock_client.models.generate_content.return_value = mock_resp

    with patch.object(gen, "_get_client", return_value=mock_client):
        req = DocumentRequest(
            document_type="Employment Contract",
            parties="Employer Inc and Employee",
            terms="Standard employment terms",
            effective_date="October 2026",
        )
        result = gen.generate_document(req)

        assert result["document_title"] == "EMPLOYMENT CONTRACT"
        assert "mocked contract agreement text" in result["content"]
        assert result["source"] == "GEMINI"
