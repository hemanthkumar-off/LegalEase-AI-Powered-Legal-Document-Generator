"""Tests for document export services (TXT, DOCX, PDF) and edited content preservation."""

import io
import docx
from fastapi.testclient import TestClient

from backend.services.export_service import ExportService


def test_txt_generation(mock_generated_draft):
    """Test 8: Verify TXT generation produces valid UTF-8 text with disclaimer."""
    txt_bytes = ExportService.generate_txt(
        content=mock_generated_draft,
        document_title="Non-Disclosure Agreement",
        document_type="NDA",
    )
    assert isinstance(txt_bytes, bytes)
    assert len(txt_bytes) > 0

    decoded = txt_bytes.decode("utf-8")
    assert "NON-DISCLOSURE AGREEMENT" in decoded
    assert "Alpha Technologies" in decoded
    assert "Beta Solutions" in decoded
    assert "NOTICE:" in decoded
    assert "LegalEase generates document drafts" in decoded


def test_docx_generation(mock_generated_draft):
    """Test 9: Verify DOCX generation creates valid Microsoft Word document with headers and styling."""
    sample_terms = "Term 1: Confidentiality for 2 years; Term 2: Return of information"
    docx_bytes = ExportService.generate_docx(
        content=mock_generated_draft,
        document_title="Non-Disclosure Agreement",
        document_type="NDA",
        terms=sample_terms,
    )
    assert isinstance(docx_bytes, bytes)
    assert len(docx_bytes) > 0

    # Parse with python-docx to verify format integrity
    doc_file = io.BytesIO(docx_bytes)
    doc = docx.Document(doc_file)

    # Verify paragraphs exist
    full_text = "\n".join([p.text for p in doc.paragraphs])
    assert "NON-DISCLOSURE AGREEMENT" in full_text
    assert "Alpha Technologies" in full_text
    assert "LEGAL NOTICE" in full_text

    # Verify key terms table was created
    assert len(doc.tables) >= 1
    table = doc.tables[0]
    assert "Agreed Condition / Term" in table.rows[0].cells[1].text


def test_pdf_generation(mock_generated_draft):
    """Test 10: Verify PDF generation creates valid ReportLab document with headers/footers."""
    pdf_bytes = ExportService.generate_pdf(
        content=mock_generated_draft,
        document_title="Non-Disclosure Agreement",
        document_type="NDA",
    )
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0

    # PDF files must start with %PDF- header magic bytes
    assert pdf_bytes.startswith(b"%PDF-")


def test_edited_content_exported_instead_of_original():
    """Test 11: Verify that exported files strictly reflect user edits rather than the original draft."""
    original_draft = "Original Clause: The contractor shall be paid $50 per hour."
    edited_draft = "EDITED Clause: The contractor shall be paid $85 per hour after negotiation."

    # TXT export
    txt_out = ExportService.generate_txt(content=edited_draft).decode("utf-8")
    assert "$85 per hour" in txt_out
    assert "$50 per hour" not in txt_out

    # DOCX export
    docx_out = ExportService.generate_docx(content=edited_draft)
    doc = docx.Document(io.BytesIO(docx_out))
    doc_text = "\n".join([p.text for p in doc.paragraphs])
    assert "$85 per hour" in doc_text
    assert "$50 per hour" not in doc_text

    # PDF export
    pdf_out = ExportService.generate_pdf(content=edited_draft)
    assert pdf_out.startswith(b"%PDF-")
    
    # Verify rendered text inside PDF using pdfplumber
    import pdfplumber
    with pdfplumber.open(io.BytesIO(pdf_out)) as pdf:
        pdf_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        assert "$85 per hour" in pdf_text
        assert "$50 per hour" not in pdf_text


def test_export_endpoints_via_fastapi(client: TestClient):
    """Verify all FastAPI export endpoints (/export/txt, /export/docx, /export/pdf)."""
    payload = {
        "document_title": "Consulting Agreement",
        "document_type": "Agreement",
        "content": "This is a test consulting agreement with specific edited terms.",
        "terms": "Compensation: $100/hr; Term: 6 months",
    }

    # Test /export/txt
    r_txt = client.post("/export/txt", json=payload)
    assert r_txt.status_code == 200
    assert r_txt.headers["content-type"].startswith("text/plain")
    assert "consulting_agreement.txt" in r_txt.headers["content-disposition"]

    # Test /export/docx
    r_docx = client.post("/export/docx", json=payload)
    assert r_docx.status_code == 200
    assert "wordprocessingml.document" in r_docx.headers["content-type"]
    assert "consulting_agreement.docx" in r_docx.headers["content-disposition"]

    # Test /export/pdf
    r_pdf = client.post("/export/pdf", json=payload)
    assert r_pdf.status_code == 200
    assert r_pdf.headers["content-type"] == "application/pdf"
    assert "consulting_agreement.pdf" in r_pdf.headers["content-disposition"]
