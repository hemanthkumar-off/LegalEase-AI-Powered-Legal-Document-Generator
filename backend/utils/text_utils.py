"""Text processing, sanitization, parsing, and filename utilities for LegalEase."""

import re
import html
from typing import List, Dict, Any


def sanitize_text(text: str) -> str:
    """Normalize and sanitize text for clean PDF, DOCX, and TXT export.

    Handles smart quotes, unicode dashes, non-breaking spaces, and unsupported
    characters while preserving legitimate legal formatting and punctuation.
    """
    if not text:
        return ""

    replacements = {
        # Smart single quotes
        "\u2018": "'",
        "\u2019": "'",
        "\u201a": "'",
        "\u201b": "'",
        "`": "'",
        # Smart double quotes
        "\u201c": '"',
        "\u201d": '"',
        "\u201e": '"',
        "\u00ab": '"',
        "\u00bb": '"',
        # Dashes
        "\u2014": " - ",
        "\u2013": " - ",
        "\u2015": " - ",
        # Spaces
        "\u00a0": " ",
        "\u200b": "",
        "\ufeff": "",
        # Bullets
        "\u2022": "*",
        "\u2023": "*",
        "\u25e6": "*",
        "\u2043": "*",
        "\uf0b7": "*",
        # Ellipsis & copyright/trade
        "\u2026": "...",
        "\u00a9": "(c)",
        "\u00ae": "(R)",
        "\u2122": "(TM)",
        # Section symbol
        "\u00a7": "Section ",
    }

    sanitized = text
    for orig, repl in replacements.items():
        sanitized = sanitized.replace(orig, repl)

    # Normalize line breaks to standard \n
    sanitized = sanitized.replace("\r\n", "\n").replace("\r", "\n")

    # Collapse excessive blank lines (> 3 into 2)
    sanitized = re.sub(r"\n{3,}", "\n\n", sanitized)

    return sanitized.strip()


def parse_terms(terms_raw: str) -> List[str]:
    """Parse terms input separated by semicolons or newlines into clean clauses."""
    if not terms_raw:
        return []

    # If text has semicolons, split by semicolon
    if ";" in terms_raw:
        parts = [p.strip() for p in terms_raw.split(";")]
    else:
        # Otherwise split by newlines
        parts = [p.strip() for p in terms_raw.splitlines()]

    # Clean leading bullets or numbers
    cleaned: List[str] = []
    for part in parts:
        part = re.sub(r"^[\*\-\•\d+\.\)]\s*", "", part).strip()
        if part:
            cleaned.append(part)
    return cleaned


def sanitize_filename(base_name: str, ext: str) -> str:
    """Create a safe, sanitized filename with the given extension."""
    clean_name = re.sub(r"[^\w\s-]", "", base_name.strip().lower())
    clean_name = re.sub(r"[-\s]+", "_", clean_name).strip("_")
    if not clean_name:
        clean_name = "legal_document"

    ext_clean = ext.lstrip(".").lower()
    return f"{clean_name}.{ext_clean}"


def parse_document_blocks(text: str) -> List[Dict[str, Any]]:
    """Parse markdown-like legal document text into structured semantic blocks.

    Blocks have a type: 'title', 'heading_1', 'heading_2', 'bullet', 'numbered', 'paragraph', 'signature'.
    """
    clean_text = sanitize_text(text)
    lines = clean_text.splitlines()
    blocks: List[Dict[str, Any]] = []

    in_signature_section = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check for signature section indicator
        if re.search(r"^(in witness whereof|signatures?|sign-off|executed as of)", stripped, re.IGNORECASE):
            in_signature_section = True
            blocks.append({"type": "heading_2", "text": stripped})
            continue

        # Title detection: # Document Title or all-caps short header
        if stripped.startswith("# ") and not stripped.startswith("## "):
            title_text = stripped[2:].strip().replace("**", "").replace("*", "")
            blocks.append({"type": "title", "text": title_text})
        elif stripped.startswith("## ") and not stripped.startswith("### "):
            h1_text = stripped[3:].strip().replace("**", "").replace("*", "")
            blocks.append({"type": "heading_1", "text": h1_text})
        elif stripped.startswith("### "):
            h2_text = stripped[4:].strip().replace("**", "").replace("*", "")
            blocks.append({"type": "heading_2", "text": h2_text})
        # Check for Section / Article headers: e.g., "SECTION 1. DEFINITIONS" or "**1. Purpose**"
        elif re.match(r"^(\*{0,2}(SECTION|ARTICLE)\s+\d+[\.\:]?|\*{0,2}\d+[\.\)]\s+[A-Z\s]{3,}\*{0,2})$", stripped, re.IGNORECASE):
            text_val = stripped.replace("**", "").replace("*", "").strip()
            blocks.append({"type": "heading_1", "text": text_val})
        elif re.match(r"^(\*{2}[A-Za-z0-9\s\,\.\-]{3,60}\*{2})$", stripped):
            # Bold stand-alone line is usually a sub-heading
            blocks.append({"type": "heading_2", "text": stripped.replace("**", "").strip()})
        # Bullet list items
        elif re.match(r"^[\*\-\•]\s+(.*)", stripped):
            match = re.match(r"^[\*\-\•]\s+(.*)", stripped)
            content = match.group(1).strip() if match else stripped
            blocks.append({"type": "bullet", "text": content})
        # Numbered list items: e.g. "1.1 Obligations" or "1. Term"
        elif re.match(r"^\d+(\.\d+)*[\.\)]\s+(.*)", stripped):
            match = re.match(r"^(\d+(\.\d+)*[\.\)])\s+(.*)", stripped)
            prefix = match.group(1) if match else ""
            content = match.group(3) if match else stripped
            blocks.append({"type": "numbered", "prefix": prefix, "text": content})
        # Signature block detection lines like "By: ____________________" or "[PARTY NAME]"
        elif in_signature_section or "signature:" in stripped.lower() or "by: ___" in stripped.lower():
            blocks.append({"type": "signature", "text": stripped})
        else:
            # Regular paragraph
            # Strip outer bolding if the whole paragraph has it for some reason
            blocks.append({"type": "paragraph", "text": stripped})

    return blocks


def format_html_preview(text: str) -> str:
    """Convert raw text to clean styled HTML for in-browser preview."""
    clean_text = sanitize_text(text)
    paragraphs = clean_text.split("\n\n")

    html_parts = []
    for p in paragraphs:
        p_clean = p.strip()
        if not p_clean:
            continue

        if p_clean.startswith("# "):
            h_text = html.escape(p_clean[2:].strip())
            html_parts.append(f"<h1 class='doc-title'>{h_text}</h1>")
        elif p_clean.startswith("## "):
            h_text = html.escape(p_clean[3:].strip())
            html_parts.append(f"<h2 class='doc-section'>{h_text}</h2>")
        elif p_clean.startswith("### "):
            h_text = html.escape(p_clean[4:].strip())
            html_parts.append(f"<h3 class='doc-subsection'>{h_text}</h3>")
        else:
            lines = p_clean.split("\n")
            if any(l.strip().startswith(("* ", "- ", "• ")) for l in lines):
                items_html = []
                for l in lines:
                    l_s = l.strip()
                    if l_s.startswith(("* ", "- ", "• ")):
                        items_html.append(f"<li>{html.escape(l_s[2:].strip())}</li>")
                    else:
                        items_html.append(f"<p>{html.escape(l_s)}</p>")
                html_parts.append(f"<ul class='doc-list'>{''.join(items_html)}</ul>")
            else:
                formatted_lines = "<br/>".join(html.escape(line) for line in lines)
                html_parts.append(f"<p class='doc-p'>{formatted_lines}</p>")

    return "\n".join(html_parts)
