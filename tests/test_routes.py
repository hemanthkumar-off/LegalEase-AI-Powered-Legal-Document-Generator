"""Unit and integration tests for FastAPI backend routes."""

from unittest.mock import patch
from fastapi.testclient import TestClient

from backend.ai_core.gemini_generator import GeminiServiceError


def test_root_endpoint(client: TestClient):
    """Test 1: Verify root endpoint returns online service status."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["app"] == "LegalEase"
    assert "endpoints" in data


def test_health_endpoint(client: TestClient):
    """Test 2: Verify health endpoint returns healthy status and model config."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "LegalEase"
    assert "gemini_model" in data


def test_generate_endpoint_success(client: TestClient, sample_nda_request, mock_generated_draft):
    """Test 3 & 6: Verify valid generation request with mocked Gemini service."""
    mock_result = {
        "document_title": "NON-DISCLOSURE AGREEMENT",
        "content": mock_generated_draft,
        "model_used": "gemini-2.5-flash",
        "source": "GEMINI",
    }

    with patch(
        "backend.services.document_service.GeminiDocumentGenerator.generate_document",
        return_value=mock_result,
    ):
        response = client.post("/generate", json=sample_nda_request)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["document_title"] == "NON-DISCLOSURE AGREEMENT"
        assert data["document_type"] == "Non-Disclosure Agreement"
        assert "Alpha Technologies" in data["content"]
        assert len(data["terms_list"]) >= 2
        assert "disclaimer" in data


def test_generate_missing_required_fields(client: TestClient):
    """Test 4: Verify request fails with 422 when required fields are missing."""
    # Missing parties
    payload_no_parties = {
        "document_type": "NDA",
        "terms": "Confidentiality for 2 years",
        "effective_date": "October 2, 2026",
    }
    response = client.post("/generate", json=payload_no_parties)
    assert response.status_code == 422

    # Missing terms
    payload_no_terms = {
        "document_type": "NDA",
        "parties": "A and B",
        "effective_date": "October 2, 2026",
    }
    response = client.post("/generate", json=payload_no_terms)
    assert response.status_code == 422


def test_generate_invalid_blank_input(client: TestClient):
    """Test 5: Verify request fails with 422 when fields contain only whitespace."""
    payload = {
        "document_type": "   ",
        "parties": "Party A and Party B",
        "terms": "Valid terms",
        "effective_date": "October 2, 2026",
    }
    response = client.post("/generate", json=payload)
    assert response.status_code == 422


def test_generate_gemini_service_failure(client: TestClient, sample_nda_request):
    """Test 7: Verify graceful error handling when Gemini service fails."""
    with patch(
        "backend.services.document_service.GeminiDocumentGenerator.generate_document",
        side_effect=GeminiServiceError(
            "Google Gemini API error: Quota exceeded",
            status_code=503,
        ),
    ):
        response = client.post("/generate", json=sample_nda_request)
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
        assert "Quota exceeded" in data["detail"]
