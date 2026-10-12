"""Tests for text sanitization, unicode normalization, term parsing, and filename helpers."""

from backend.utils.text_utils import (
    sanitize_text,
    sanitize_filename,
    parse_terms,
    parse_document_blocks,
    format_html_preview,
)


def test_filename_sanitization():
    """Test 12: Verify filename sanitization removes illegal characters and formats cleanly."""
    assert sanitize_filename("Non-Disclosure Agreement", "docx") == "non_disclosure_agreement.docx"
    assert sanitize_filename("Employment Offer Letter #2 (2026)", "pdf") == "employment_offer_letter_2_2026.pdf"
    assert sanitize_filename("Special / Contract * Test!?", "txt") == "special_contract_test.txt"
    assert sanitize_filename("   ", "pdf") == "legal_document.pdf"


def test_sanitize_text_smart_quotes_and_dashes():
    """Verify typographic quotes, dashes, and non-breaking spaces are normalized."""
    raw = "“This agreement” is ‘confidential’ — and costs $500–$600.\u00a0Includes \u2022 bullet."
    sanitized = sanitize_text(raw)
    assert '"This agreement"' in sanitized
    assert "'confidential'" in sanitized
    assert " - " in sanitized
    assert "* bullet" in sanitized


def test_parse_terms_semicolon_and_newline():
    """Verify term parser handles both semicolon and newline delimited clauses."""
    # Semicolon delimited
    raw_semi = "Clause 1: Pay on time; Clause 2: Keep secret; Clause 3: 30 days notice"
    parsed_semi = parse_terms(raw_semi)
    assert len(parsed_semi) == 3
    assert parsed_semi[0] == "Clause 1: Pay on time"
    assert parsed_semi[1] == "Clause 2: Keep secret"
    assert parsed_semi[2] == "Clause 3: 30 days notice"

    # Newline delimited with bullets
    raw_lines = "* Term A: Do work\n- Term B: Get paid\n• Term C: Sign contract"
    parsed_lines = parse_terms(raw_lines)
    assert len(parsed_lines) == 3
    assert parsed_lines[0] == "Term A: Do work"
    assert parsed_lines[1] == "Term B: Get paid"
    assert parsed_lines[2] == "Term C: Sign contract"


def test_parse_document_blocks():
    """Verify parser detects titles, headings, bullets, and paragraphs."""
    sample = (
        "# MAIN TITLE\n\n"
        "## 1. FIRST SECTION\n\n"
        "This is a paragraph explaining obligations.\n\n"
        "* First obligation\n"
        "* Second obligation\n\n"
        "Signatures:\n"
        "By: ____________________\n"
    )
    blocks = parse_document_blocks(sample)
    types = [b["type"] for b in blocks]

    assert "title" in types
    assert "heading_1" in types
    assert "paragraph" in types
    assert "bullet" in types
    assert "signature" in types


def test_format_html_preview():
    """Verify format_html_preview produces styled HTML markup."""
    text = "# NDA\n\nParagraph text here."
    html_out = format_html_preview(text)
    assert "<h1 class='doc-title'>NDA</h1>" in html_out
    assert "<p class='doc-p'>Paragraph text here.</p>" in html_out
