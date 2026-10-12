"""Gemini AI Core integration for LegalEase.

Uses the official Google GenAI Python SDK (`google.genai`) to generate
professional, customized legal document drafts based on user inputs.
"""

import os
import time
import logging
from typing import Optional, Dict, Any

from google import genai
from google.genai import types
from google.genai.errors import APIError

from backend.config import settings
from backend.schemas import DocumentRequest

logger = logging.getLogger("LegalEase.AI")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class GeminiServiceError(Exception):
    """Exception raised when document generation via Gemini fails."""

    def __init__(self, message: str, status_code: int = 500, details: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class GeminiDocumentGenerator:
    """Orchestrates communication with the Google Gemini API for legal draft creation."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL
        self._client: Optional[genai.Client] = None

    def _get_client(self) -> genai.Client:
        """Initialize or retrieve the GenAI client."""
        if not self.api_key or not self.api_key.strip():
            raise GeminiServiceError(
                "Gemini API key is not configured. Please set GEMINI_API_KEY in your .env file.",
                status_code=401,
            )

        if self._client is None:
            try:
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini Client: {str(e)}")
                raise GeminiServiceError(
                    f"Failed to initialize Gemini API client: {str(e)}",
                    status_code=500,
                )
        return self._client

    def build_system_instruction(self) -> str:
        """Construct the system instruction enforcing legal drafting guidelines and preventing hallucinations."""
        return (
            "You are LegalEase AI, an expert legal drafting assistant specialized in generating "
            "comprehensive, professional, and well-structured legal document drafts.\n\n"
            "CRITICAL DRAFTING RULES:\n"
            "1. ADAPTIVE STRUCTURE: Structure the agreement logically according to the document type "
            "(e.g., Non-Disclosure Agreement, Residential Lease, Employment Contract, Freelance Agreement). "
            "Include customary sections: Title, Effective Date, Parties & Recitals, Definitions, "
            "Core Obligations/Terms, Term & Termination, Governing Law, Dispute Resolution, "
            "and Signature Blocks.\n"
            "2. NO FACTUAL HALLUCINATIONS: Do NOT invent factual details that the user did not provide "
            "(e.g., specific monetary amounts, addresses, phone numbers, employee job titles, dates, or company registration numbers). "
            "If any specific factual detail is customary but missing, use CLEAR BRACKETED PLACEHOLDERS "
            "such as [EMPLOYEE ADDRESS], [SALARY AMOUNT], [PROPERTY ADDRESS], [SECURITY DEPOSIT AMOUNT], or [GOVERNING JURISDICTION].\n"
            "3. RESPECT ALL USER TERMS: Integrate every term, clause, and condition provided by the user into the draft accurately.\n"
            "4. PROFESSIONAL FORMATTING: Use clean Markdown with clear headings (# Title, ## Section, ### Subsection), "
            "numbered clauses (e.g. 1.1, 1.2), bullet points, and distinct signature blocks at the end.\n"
            "5. LEGAL DISCLAIMER: Draft as a comprehensive contract/agreement template. "
            "Do NOT claim to be a licensed attorney or provide guaranteed legal advice."
        )

    def build_prompt(self, request: DocumentRequest) -> str:
        """Construct the user prompt incorporating all supplied details."""
        prompt_parts = [
            f"Please generate a complete, professional, and legally sound draft for the following legal document:\n",
            f"DOCUMENT TYPE: {request.document_type}",
            f"PARTIES INVOLVED:\n{request.parties}",
            f"EFFECTIVE DATE: {request.effective_date}",
            f"TERMS & CONDITIONS / KEY CLAUSES:\n{request.terms}",
        ]

        if request.jurisdiction and request.jurisdiction.strip():
            prompt_parts.append(f"GOVERNING JURISDICTION: {request.jurisdiction.strip()}")
        else:
            prompt_parts.append("GOVERNING JURISDICTION: [Insert Governing State / Country / Jurisdiction]")

        if request.additional_instructions and request.additional_instructions.strip():
            prompt_parts.append(f"ADDITIONAL INSTRUCTIONS & PREFERENCES:\n{request.additional_instructions.strip()}")

        prompt_parts.append(
            "\nPlease draft the full text of the document from title to signature lines. "
            "Ensure the clauses are clearly numbered and organized under logical headings. "
            "Do not truncate or summarize; provide the full, ready-to-customize contract text."
        )

        return "\n\n".join(prompt_parts)

    def _build_fallback_document(self, request: DocumentRequest, reason: Optional[str] = None) -> Dict[str, Any]:
        """Construct a high-quality, comprehensive legal agreement draft when Gemini is unavailable or unconfigured."""
        from backend.utils.text_utils import parse_terms

        doc_type = request.document_type.strip()
        doc_title = doc_type.upper()
        parsed_terms = parse_terms(request.terms)
        parties_lines = [p.strip() for p in request.parties.splitlines() if p.strip()]
        if not parties_lines:
            parties_lines = [request.parties.strip()]

        jurisdiction = request.jurisdiction.strip() if request.jurisdiction else "[Insert Governing State / Country / Jurisdiction]"

        # Build comprehensive clauses
        lines = [
            f"# {doc_title}",
            "",
            f"This {doc_type} (the 'Agreement') is entered into and made effective as of **{request.effective_date}** (the 'Effective Date'), by and between:",
            "",
        ]

        for p in parties_lines:
            lines.append(f"* **{p}**")

        lines.extend([
            "",
            "## 1. BACKGROUND AND RECITALS",
            f"WHEREAS, the parties desire to establish the terms and mutual commitments governing their relationship with respect to the matters described herein, particularly concerning {doc_type.lower()};",
            "WHEREAS, each party has agreed to the covenants, obligations, and terms set forth in this Agreement for good and valuable consideration, the receipt and sufficiency of which are hereby acknowledged.",
            "",
            "NOW, THEREFORE, the parties mutually agree as follows:",
            "",
            "## 2. AGREED TERMS & CORE COVENANTS",
        ])

        if parsed_terms:
            for idx, term in enumerate(parsed_terms, 1):
                lines.append(f"**2.{idx} Clause {idx}**: {term}")
                lines.append("")
        else:
            lines.append(f"2.1 The parties agree to abide by the covenants and conditions specified herein.")
            lines.append("")

        # Adaptive sections based on document type
        lower_type = doc_type.lower()
        if "disclosure" in lower_type or "nda" in lower_type:
            lines.extend([
                "## 3. CONFIDENTIALITY AND NON-DISCLOSURE OBLIGATIONS",
                "3.1 **Scope of Confidential Information**: Confidential Information includes all technical, commercial, financial, and operational data, whether disclosed orally or in writing.",
                "3.2 **Standard of Care**: The Receiving Party agrees to maintain the highest standard of reasonable care to safeguard the confidential nature of the disclosed information.",
                "3.3 **Exclusions**: Confidential Information shall not include information that is publicly known through no breach of this Agreement, or was already known to the Receiving Party prior to disclosure.",
                "3.4 **Return or Destruction**: Upon written request or termination of discussions, all copies of Confidential Information shall be promptly returned or securely destroyed.",
                "",
            ])
        elif "employ" in lower_type or "offer" in lower_type:
            lines.extend([
                "## 3. DUTIES, COMPENSATION & AT-WILL STATUS",
                "3.1 **Performance of Duties**: The Employee agrees to devote their professional time, attention, and energies faithfully and diligently to the performance of assigned responsibilities.",
                "3.2 **Compensation & Benefits**: Compensation shall be payable in accordance with the Employer's standard payroll schedules, subject to applicable statutory tax withholdings.",
                "3.3 **Proprietary Rights & Inventions**: All intellectual property, designs, patents, trademarks, and trade secrets authored or invented during employment shall remain the sole and exclusive property of the Employer.",
                "3.4 **At-Will Employment**: Employment remains at-will unless explicitly superseded by written mutual contract.",
                "",
            ])
        elif "lease" in lower_type or "rent" in lower_type:
            lines.extend([
                "## 3. LEASE TERMS, OCCUPANCY & MAINTENANCE",
                "3.1 **Condition of Premises**: Tenant agrees to maintain the premises in a clean, sanitary, and lawful condition throughout the entire term.",
                "3.2 **Rent and Security Deposit**: Rent is payable on or before the due date agreed herein. The Security Deposit shall be maintained in accordance with applicable local tenancy laws.",
                "3.3 **Quiet Enjoyment & Subletting**: Tenant shall not assign, transfer, or sublet any portion of the demised premises without prior written authorization from the Landlord.",
                "",
            ])
        else:
            lines.extend([
                "## 3. MUTUAL RIGHTS AND OBLIGATIONS",
                "3.1 **Standard of Performance**: Each party covenants to perform its obligations with the highest standard of professional care and good faith.",
                "3.2 **Representations and Warranties**: Each party warrants that it has full legal capacity and corporate authority to execute, deliver, and perform this Agreement.",
                "",
            ])

        if request.additional_instructions and request.additional_instructions.strip():
            lines.extend([
                "## 4. SPECIAL CLAUSES AND ADDITIONAL PROVISIONS",
                f"4.1 **Special Stipulations**: {request.additional_instructions.strip()}",
                "",
                "## 5. GOVERNING LAW AND DISPUTE RESOLUTION",
            ])
        else:
            lines.extend([
                "## 4. GOVERNING LAW AND DISPUTE RESOLUTION",
            ])

        lines.extend([
            f"This Agreement shall be construed, interpreted, and governed in accordance with the substantive laws of **{jurisdiction}**, without regard to conflict of law principles.",
            "Any unresolved dispute or claim arising under this Agreement shall first be submitted to good-faith mediation before initiating formal court proceedings.",
            "",
            "## 5. GENERAL PROVISIONS",
            "5.1 **Entire Agreement**: This document constitutes the entire agreement between the parties regarding its subject matter and supersedes all prior understandings or negotiations.",
            "5.2 **Severability**: If any provision of this Agreement is held to be invalid or unenforceable, the remaining provisions shall continue in full force and effect.",
            "5.3 **Counterparts**: This Agreement may be executed in counterparts, each of which shall be deemed an original.",
            "",
            "## 6. SIGNATURE BLOCKS",
            "IN WITNESS WHEREOF, the duly authorized representatives of the parties have executed this Agreement as of the Effective Date.",
            "",
        ])

        for p in parties_lines:
            lines.extend([
                f"**{p}**",
                "By: ___________________________________",
                "Name: [AUTHORIZED SIGNATORY]",
                "Title: [OFFICIAL TITLE]",
                "Date: _________________________________",
                "",
            ])

        full_content = "\n".join(lines)
        notice_msg = (
            f"Generated using LegalEase Built-in Legal Drafting Engine (Offline / Demo Mode)"
            + (f" due to: {reason}." if reason else ". Configure a valid GEMINI_API_KEY in .env for live Gemini AI generation.")
        )

        return {
            "document_title": doc_title,
            "content": full_content,
            "model_used": "legalease-engine (Built-in Mode)",
            "source": "FALLBACK",
            "notice": notice_msg,
        }

    def generate_document(self, request: DocumentRequest) -> Dict[str, Any]:
        """Generate a complete legal document draft using Gemini with graceful fallback."""
        # Development audit logging (safely excludes API keys)
        logger.info("========================================")
        logger.info("LEGALEASE AI REQUEST")
        logger.info(f"Document Type: {request.document_type}")
        logger.info("AI Provider: Google Gemini")
        logger.info(f"Configured Model: {self.model_name}")
        logger.info("========================================")

        # Check if API key is configured and appears plausible
        if not self.api_key or not self.api_key.strip() or self.api_key.startswith("AQ.") or "your_" in self.api_key:
            logger.info("Gemini API key not configured or contains placeholder/expired OAuth token.")
            logger.info("Activating LegalEase Built-in Drafting Engine.")
            return self._build_fallback_document(
                request,
                reason="Gemini API key is not configured or requires an active Google AI Studio key"
            )

        system_instruction = self.build_system_instruction()
        user_prompt = self.build_prompt(request)

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.3,  # Low temperature for formal legal consistency
            top_p=0.9,
            max_output_tokens=4096,
        )

        last_error = None
        max_retries = max(1, settings.GEMINI_MAX_RETRIES)

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Gemini API call attempt {attempt}/{max_retries}: STARTED")
                client = self._get_client()
                start_time = time.time()
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config=config,
                )
                elapsed = time.time() - start_time

                generated_text = response.text if response and response.text else ""

                if not generated_text or not generated_text.strip():
                    raise GeminiServiceError("Gemini returned an empty response. Please retry.", status_code=502)

                logger.info("Gemini API call: SUCCESS")
                logger.info(f"Response source: GEMINI (Model: {self.model_name})")
                logger.info(f"Duration: {elapsed:.2f}s | Output length: {len(generated_text)} characters")
                logger.info("========================================")

                first_line = generated_text.strip().splitlines()[0].replace("#", "").strip()
                document_title = first_line if first_line else request.document_type

                return {
                    "document_title": document_title,
                    "content": generated_text.strip(),
                    "model_used": self.model_name,
                    "source": "GEMINI",
                    "notice": None,
                }

            except APIError as e:
                last_error = e
                logger.warning(f"Gemini API attempt {attempt} failed with APIError: {e.message} (Code: {e.code})")
                if e.code in (401, 403):
                    # Authentication failure - immediately fall back cleanly
                    logger.warning("Authentication failed. Falling back to built-in drafting engine.")
                    return self._build_fallback_document(
                        request,
                        reason=f"Google Gemini authentication failed ({e.message})"
                    )
                time.sleep(1)

            except Exception as e:
                last_error = e
                logger.warning(f"Gemini API call attempt {attempt} failed: {str(e)}")
                time.sleep(1)

        # If retries exhausted or network failed, gracefully fall back instead of breaking the app
        logger.warning(f"Gemini API unavailable after {max_retries} attempts ({str(last_error)}).")
        logger.info("Activating LegalEase Built-in Drafting Engine fallback.")
        return self._build_fallback_document(
            request,
            reason=f"Google Gemini connection was unreachable ({str(last_error)})"
        )
