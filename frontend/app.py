"""LegalEase - Streamlit Frontend Application.

Provides a modern, responsive web UI for drafting, previewing,
editing, and exporting legal documents powered by Google Gemini and FastAPI.
"""

import os
import io
import time
from datetime import date
from typing import Dict, Any, Optional

import requests
import streamlit as st

# Configure Streamlit page settings
st.set_page_config(
    page_title="LegalEase – AI-Powered Legal Document Generator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Backend URL configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

# Custom CSS for Glassmorphism Theme (Black, White, Violet, and Yellow)
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Glassmorphism Atmospheric Background: Pitch Black with Violet and Golden-Yellow Aurora */
.stApp {
    background-color: #06050a;
    background-image: 
        radial-gradient(circle at 12% 18%, rgba(124, 58, 237, 0.22) 0%, transparent 45%),
        radial-gradient(circle at 88% 12%, rgba(234, 179, 8, 0.14) 0%, transparent 40%),
        radial-gradient(circle at 50% 85%, rgba(147, 51, 234, 0.16) 0%, #06050a 100%);
    background-attachment: fixed;
    color: #ffffff;
}

/* Universal Glassmorphic Card */
.glass-panel {
    background: rgba(18, 14, 28, 0.58);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-top: 1px solid rgba(255, 255, 255, 0.22);
    backdrop-filter: blur(20px) saturate(190%);
    -webkit-backdrop-filter: blur(20px) saturate(190%);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 12px 35px -8px rgba(0, 0, 0, 0.65), 0 0 20px -3px rgba(124, 58, 237, 0.18);
}

/* Disclaimer Notice Card: Glass with Gold/Yellow Accent */
.disclaimer-card {
    background: rgba(234, 179, 8, 0.08);
    border-left: 4px solid #facc15;
    border: 1px solid rgba(250, 204, 21, 0.25);
    border-left-width: 5px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 12px;
    padding: 14px 20px;
    margin-bottom: 24px;
    font-size: 0.90rem;
    color: #fef08a;
    line-height: 1.55;
    box-shadow: 0 8px 25px rgba(234, 179, 8, 0.08);
}

.disclaimer-card strong {
    color: #ffffff;
}

/* Brand Header */
.brand-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 6px;
}

.brand-title {
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -0.8px;
    background: linear-gradient(135deg, #ffffff 15%, #c084fc 55%, #fde047 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    text-shadow: 0 0 35px rgba(192, 132, 252, 0.35);
}

.brand-subtitle {
    color: #e2e8f0;
    font-size: 1.05rem;
    font-weight: 400;
    margin-top: 4px;
    margin-bottom: 22px;
}

.brand-subtitle span.highlight-violet {
    color: #c084fc;
    font-weight: 600;
}

.brand-subtitle span.highlight-yellow {
    color: #fde047;
    font-weight: 600;
}

/* Document preview viewport with Smoky Glass */
.preview-container {
    background: rgba(10, 8, 18, 0.75);
    border: 1px solid rgba(168, 85, 247, 0.28);
    border-top: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 14px;
    padding: 34px 44px;
    color: #f8fafc;
    line-height: 1.75;
    max-height: 600px;
    overflow-y: auto;
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    box-shadow: inset 0 2px 16px rgba(0, 0, 0, 0.7), 0 10px 40px rgba(0, 0, 0, 0.5);
    font-family: 'Georgia', serif;
}

.preview-container h1 {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #fde047;
    font-size: 1.65rem;
    font-weight: 700;
    text-align: center;
    border-bottom: 1px solid rgba(168, 85, 247, 0.35);
    padding-bottom: 14px;
    margin-bottom: 24px;
    text-shadow: 0 0 15px rgba(253, 224, 71, 0.25);
}

.preview-container h2 {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #e9d5ff;
    font-size: 1.25rem;
    font-weight: 600;
    margin-top: 22px;
    margin-bottom: 12px;
}

.preview-container h3 {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #fef08a;
    font-size: 1.1rem;
    margin-top: 16px;
    margin-bottom: 8px;
}

.preview-container ul {
    margin-left: 24px;
    color: #f1f5f9;
}

.preview-container p {
    color: #e2e8f0;
}

/* Sidebar Glassmorphism */
[data-testid="stSidebar"] {
    background-color: rgba(9, 7, 16, 0.78) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border-right: 1px solid rgba(168, 85, 247, 0.22) !important;
    box-shadow: 4px 0 25px rgba(0, 0, 0, 0.5) !important;
}

/* Form Input Elements (Inputs, Selectboxes, Textareas) - Glass Style */
input, textarea, [data-baseweb="select"] > div {
    background-color: rgba(22, 17, 36, 0.65) !important;
    border: 1px solid rgba(168, 85, 247, 0.32) !important;
    color: #ffffff !important;
    border-radius: 10px !important;
    backdrop-filter: blur(14px) !important;
    transition: all 0.25s ease-in-out !important;
}

input:focus, textarea:focus, [data-baseweb="select"] > div:focus-within {
    border-color: #fde047 !important;
    box-shadow: 0 0 14px rgba(253, 224, 71, 0.32), inset 0 1px 2px rgba(0,0,0,0.4) !important;
}

/* Labels */
label, [data-testid="stWidgetLabel"] {
    color: #f8fafc !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
}

/* Primary Button (Violet to Yellow Radiant Gradient) */
[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #7c3aed 0%, #9333ea 50%, #eab308 100%) !important;
    color: #ffffff !important;
    border: 1px solid rgba(254, 240, 138, 0.45) !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    padding: 12px 24px !important;
    box-shadow: 0 4px 22px rgba(124, 58, 237, 0.45), 0 0 14px rgba(234, 179, 8, 0.3) !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

[data-testid="stBaseButton-primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(124, 58, 237, 0.65), 0 0 24px rgba(253, 224, 71, 0.55) !important;
    border-color: #fde047 !important;
    color: #ffffff !important;
}

/* Secondary Buttons - Frosted Glass with Violet & Yellow Hover */
[data-testid="stBaseButton-secondary"] {
    background: rgba(139, 92, 246, 0.14) !important;
    border: 1px solid rgba(168, 85, 247, 0.35) !important;
    color: #ffffff !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
    backdrop-filter: blur(12px) !important;
    transition: all 0.2s ease-in-out !important;
}

[data-testid="stBaseButton-secondary"]:hover {
    background: rgba(234, 179, 8, 0.18) !important;
    border-color: #facc15 !important;
    color: #fef08a !important;
    box-shadow: 0 0 15px rgba(250, 204, 21, 0.3) !important;
    transform: translateY(-1px) !important;
}

/* Download Buttons - Golden Highlight Glow */
div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, rgba(124, 58, 237, 0.25) 0%, rgba(234, 179, 8, 0.25) 100%) !important;
    border: 1px solid rgba(250, 204, 21, 0.4) !important;
    color: #ffffff !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
    transition: all 0.2s ease-in-out !important;
}

div[data-testid="stDownloadButton"] > button:hover {
    background: linear-gradient(135deg, #7c3aed 0%, #eab308 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 6px 22px rgba(250, 204, 21, 0.45) !important;
    transform: translateY(-2px) !important;
}

/* Tabs Styling */
[data-baseweb="tab-list"] {
    background: rgba(20, 16, 32, 0.5) !important;
    padding: 6px !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    gap: 8px !important;
}

[data-baseweb="tab"] {
    color: #cbd5e1 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

[aria-selected="true"] {
    background: rgba(124, 58, 237, 0.35) !important;
    color: #fde047 !important;
    border: 1px solid rgba(250, 204, 21, 0.35) !important;
    box-shadow: 0 0 15px rgba(124, 58, 237, 0.35) !important;
}

/* Status Pill: Glowing Violet-Yellow */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.80rem;
    font-weight: 600;
}
.status-online {
    background: rgba(250, 204, 21, 0.12);
    color: #fde047;
    border: 1px solid rgba(250, 204, 21, 0.4);
    box-shadow: 0 0 10px rgba(250, 204, 21, 0.2);
}
.status-offline {
    background: rgba(239, 68, 68, 0.15);
    color: #fca5a5;
    border: 1px solid rgba(239, 68, 68, 0.4);
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def check_backend_health() -> Dict[str, Any]:
    """Check health of the FastAPI backend."""
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=3)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return {"status": "offline", "gemini_configured": False, "gemini_model": "Unknown"}


def load_preset(scenario_idx: int):
    """Load sample preset scenarios from the specification into session state."""
    if scenario_idx == 1:
        # Scenario 1: Employment Contract
        st.session_state["doc_type_choice"] = "Employment Contract"
        st.session_state["parties"] = (
            "Apex Innovations Inc., a Delaware corporation (Employer)\n"
            "Alex Morgan, residing in Austin, Texas (Employee)"
        )
        st.session_state["effective_date_str"] = "October 15, 2026"
        st.session_state["jurisdiction"] = "State of Texas, USA"
        st.session_state["terms"] = (
            "Position: Senior Full-Stack AI Engineer;\n"
            "Duties include architecture design, coding, code reviews, and technical leadership;\n"
            "Annual base salary of $135,000 paid bi-weekly;\n"
            "Eligible for health insurance, 401(k) matching up to 4%, and 20 days PTO annually;\n"
            "At-will employment relationship subject to 14 days written notice by either party;\n"
            "Strict confidentiality of proprietary trade secrets, algorithms, and source code during and after employment;\n"
            "All intellectual property and inventions developed during work belong exclusively to Employer"
        )
        st.session_state["additional_instructions"] = (
            "Include standard non-solicitation of clients/employees for 12 months post-termination."
        )

    elif scenario_idx == 2:
        # Scenario 2: Non-Disclosure Agreement
        st.session_state["doc_type_choice"] = "Non-Disclosure Agreement"
        st.session_state["parties"] = (
            "Alpha Technologies Inc. (Disclosing Party)\n"
            "Beta Solutions LLC (Receiving Party)"
        )
        st.session_state["effective_date_str"] = "October 2, 2026"
        st.session_state["jurisdiction"] = "State of California, USA"
        st.session_state["terms"] = (
            "Confidential information must not be disclosed or shared with any third party;\n"
            "Information may only be used for the evaluation of a potential joint venture project;\n"
            "Confidentiality obligations remain in effect for a period of 2 years from disclosure;\n"
            "Standard exclusions apply for publicly known info or court-ordered subpoenas;\n"
            "Prompt return or certified destruction of confidential data upon written request"
        )
        st.session_state["additional_instructions"] = (
            "Include mutual remedy of injunctive relief in the event of unauthorized breach."
        )

    elif scenario_idx == 3:
        # Scenario 3: Residential Lease Agreement
        st.session_state["doc_type_choice"] = "Residential Lease Agreement"
        st.session_state["parties"] = (
            "Robert H. Vance (Landlord)\n"
            "Sarah Jenkins & David Jenkins (Tenants)"
        )
        st.session_state["effective_date_str"] = "November 1, 2026"
        st.session_state["jurisdiction"] = "State of New York, USA"
        st.session_state["terms"] = (
            "Premises located at 742 Evergreen Terrace, Apt 4B, New York, NY;\n"
            "Fixed term of 12 calendar months ending October 31, 2027;\n"
            "Monthly rent of $2,400 due on or before the 1st day of each month;\n"
            "Security deposit of $2,400 held in an escrow account;\n"
            "Late fee of $75 applied for payments received after the 5th day;\n"
            "No subletting without prior written consent from Landlord;\n"
            "Tenant responsible for gas and electric utilities; Landlord covers water and trash"
        )
        st.session_state["additional_instructions"] = (
            "Include a pet policy allowing one domestic cat with a $250 non-refundable pet deposit."
        )


# Initialize session state variables
if "doc_content" not in st.session_state:
    st.session_state["doc_content"] = ""
if "original_content" not in st.session_state:
    st.session_state["original_content"] = ""
if "doc_title" not in st.session_state:
    st.session_state["doc_title"] = ""
if "doc_type" not in st.session_state:
    st.session_state["doc_type"] = "Non-Disclosure Agreement"
if "effective_date" not in st.session_state:
    st.session_state["effective_date"] = ""
if "terms_raw" not in st.session_state:
    st.session_state["terms_raw"] = ""
if "parties_raw" not in st.session_state:
    st.session_state["parties_raw"] = ""
if "generation_success" not in st.session_state:
    st.session_state["generation_success"] = False


# =========================================================================
# SIDEBAR
# =========================================================================
with st.sidebar:
    st.markdown("### ⚖️ LegalEase")
    st.caption("AI-Powered Legal Drafting System")
    st.markdown("---")

    # Backend Health Check
    health = check_backend_health()
    if health.get("status") == "healthy":
        st.markdown(
            '<div class="status-pill status-online">● Backend Online</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-pill status-offline">● Backend Offline</div>',
            unsafe_allow_html=True,
        )
        st.warning(
            f"Cannot reach FastAPI server at `{BACKEND_URL}`. "
            "Please ensure the backend is running via `uvicorn backend.main:app --reload`."
        )

    st.markdown("---")
    st.markdown("#### ⚡ Quick Preset Scenarios")
    st.caption("Click to auto-populate fields with specification test cases:")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if st.button("Employment", use_container_width=True, help="Load Employment Contract Scenario"):
            load_preset(1)
            st.rerun()
    with col_p2:
        if st.button("NDA", use_container_width=True, help="Load NDA Scenario"):
            load_preset(2)
            st.rerun()

    if st.button("Residential Lease", use_container_width=True, help="Load Lease Agreement Scenario"):
        load_preset(3)
        st.rerun()

    st.markdown("---")
    st.markdown("#### ℹ️ System Details")
    model_name = health.get("gemini_model", "gemini-2.5-flash")
    st.markdown(f"**AI Engine:** Google Gemini")
    st.markdown(f"**Model:** `{model_name}`")
    st.markdown(f"**Backend API:** FastAPI")
    st.markdown(f"**Exporters:** TXT, DOCX, PDF")

    st.markdown("---")
    if st.button("Clear Document & Reset", use_container_width=True):
        st.session_state["doc_content"] = ""
        st.session_state["original_content"] = ""
        st.session_state["generation_success"] = False
        st.rerun()


# =========================================================================
# MAIN CONTENT HEADER
# =========================================================================
st.markdown(
    """
    <div class="brand-header">
        <h1 class="brand-title">⚖️ LegalEase</h1>
    </div>
    <div class="brand-subtitle">
        AI-Powered Legal Document Generator — <span class="highlight-violet">Draft</span>, <span class="highlight-yellow">Customize</span>, and <span class="highlight-violet">Export</span> Professional Legal Agreements.
    </div>
    <div class="disclaimer-card">
        <strong>⚖️ Educational Notice:</strong> LegalEase generates document drafts for informational and educational purposes. 
        Generated content is not formal legal advice. Consider consulting a licensed legal professional for high-stakes agreements.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================================
# INPUT FORM
# =========================================================================
with st.container():
    st.markdown("### 📋 <span style='color:#FDE047;'>Document</span> <span style='color:#C084FC;'>Configuration</span>", unsafe_allow_html=True)

    doc_types = [
        "Non-Disclosure Agreement",
        "Employment Contract",
        "Residential Lease Agreement",
        "Freelance/Service Agreement",
        "General Contract",
        "Business Agreement",
        "Employment Offer Letter",
        "Other / Custom Document",
    ]

    # Current selected doc type
    default_doc_type = st.session_state.get("doc_type_choice", "Non-Disclosure Agreement")
    doc_type_index = doc_types.index(default_doc_type) if default_doc_type in doc_types else 0

    col1, col2 = st.columns([1, 1])

    with col1:
        selected_type = st.selectbox(
            "Document Type *",
            options=doc_types,
            index=doc_type_index,
            help="Choose standard agreement type or select Custom.",
        )
        if selected_type == "Other / Custom Document":
            custom_doc_type = st.text_input(
                "Enter Custom Document Name *",
                value=st.session_state.get("custom_doc_type", "Partnership Agreement"),
            )
            active_doc_type = custom_doc_type.strip()
        else:
            active_doc_type = selected_type

        parties_input = st.text_area(
            "Parties Involved *",
            value=st.session_state.get("parties", ""),
            height=110,
            placeholder="e.g. John Doe (Freelancer), TechCorp LLC (Client)",
            help="Names, roles, and addresses/entities of all participating parties.",
        )

    with col2:
        effective_date_input = st.text_input(
            "Effective Date *",
            value=st.session_state.get(
                "effective_date_str", date.today().strftime("%B %d, %Y")
            ),
            help="Date from which the terms and obligations take legal effect.",
        )

        jurisdiction_input = st.text_input(
            "Governing Jurisdiction (Optional)",
            value=st.session_state.get("jurisdiction", ""),
            placeholder="e.g. State of California, United States",
            help="State, province, or country whose laws govern this agreement.",
        )

    terms_input = st.text_area(
        "Terms & Conditions / Key Clauses * (Use semicolons ';' or newlines to separate clauses)",
        value=st.session_state.get("terms", ""),
        height=140,
        placeholder=(
            "Payment to be made within 30 days of invoice;\n"
            "Confidentiality must be maintained for 2 years;\n"
            "Either party may terminate with 15 days written notice"
        ),
        help="Specify the substantive rules, commitments, deadlines, and terms.",
    )

    additional_input = st.text_input(
        "Additional Instructions or Special Clauses (Optional)",
        value=st.session_state.get("additional_instructions", ""),
        placeholder="e.g. Include binding arbitration and waive jury trial.",
        help="Special preferences or drafting rules for Gemini AI.",
    )

    generate_clicked = st.button(
        "⚡ Generate Legal Document Draft",
        type="primary",
        use_container_width=True,
    )


# =========================================================================
# GENERATION HANDLER
# =========================================================================
if generate_clicked:
    # Validation
    if not active_doc_type.strip():
        st.error("Please provide a valid Document Type.")
    elif not parties_input.strip():
        st.error("Please specify the Parties Involved.")
    elif not terms_input.strip():
        st.error("Please specify at least one Term or Condition.")
    elif not effective_date_input.strip():
        st.error("Please provide an Effective Date.")
    else:
        payload = {
            "document_type": active_doc_type.strip(),
            "parties": parties_input.strip(),
            "terms": terms_input.strip(),
            "effective_date": effective_date_input.strip(),
            "jurisdiction": jurisdiction_input.strip() if jurisdiction_input.strip() else None,
            "additional_instructions": (
                additional_input.strip() if additional_input.strip() else None
            ),
        }

        with st.spinner("⚖️ Generating your legal document with Google Gemini AI..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=90,
                )

                if response.status_code == 200:
                    data = response.json()
                    st.session_state["doc_content"] = data.get("content", "")
                    st.session_state["original_content"] = data.get("content", "")
                    st.session_state["doc_title"] = data.get("document_title", active_doc_type)
                    st.session_state["doc_type"] = active_doc_type
                    st.session_state["effective_date"] = effective_date_input.strip()
                    st.session_state["terms_raw"] = terms_input.strip()
                    st.session_state["parties_raw"] = parties_input.strip()
                    st.session_state["source"] = data.get("source", "GEMINI")
                    st.session_state["notice"] = data.get("notice")
                    st.session_state["generation_success"] = True
                    st.success("✅ Document Generated Successfully!")
                else:
                    err_detail = "Server error"
                    try:
                        err_detail = response.json().get("detail", response.text)
                    except Exception:
                        pass
                    st.error(f"Generation Failed ({response.status_code}): {err_detail}")

            except requests.exceptions.ConnectionError:
                st.error(
                    f"⚠️ Connection Error: Unable to contact FastAPI backend at `{BACKEND_URL}`. "
                    "Make sure the backend is running (`uvicorn backend.main:app --reload`)."
                )
            except Exception as e:
                st.error(f"⚠️ An unexpected error occurred: {str(e)}")


# =========================================================================
# DOCUMENT PREVIEW, EDITING, AND EXPORT
# =========================================================================
if st.session_state.get("doc_content"):
    st.markdown("---")
    st.markdown("### 📄 <span style='color:#FDE047;'>Generated Document</span> <span style='color:#C084FC;'>Workspace</span>", unsafe_allow_html=True)

    tab_preview, tab_edit, tab_export = st.tabs([
        "👁️ Document Preview",
        "✏️ Edit Document",
        "📥 Export & Download",
    ])

    # ---------------------------------------------------------------------
    # TAB 1: PREVIEW
    # ---------------------------------------------------------------------
    with tab_preview:
        if st.session_state.get("notice"):
            st.info(f"ℹ️ **Generator Information:** {st.session_state['notice']}")
        st.caption("Structured preview of your current document draft:")
        st.markdown(
            f'<div class="preview-container">',
            unsafe_allow_html=True,
        )
        st.markdown(st.session_state["doc_content"])
        st.markdown("</div>", unsafe_allow_html=True)

        col_nav1, col_nav2 = st.columns([1, 5])
        with col_nav1:
            st.info("💡 To make changes, switch to the **✏️ Edit Document** tab.")

    # ---------------------------------------------------------------------
    # TAB 2: EDITING
    # ---------------------------------------------------------------------
    with tab_edit:
        st.markdown("#### ✏️ Customize & Modify Document Content")
        st.caption(
            "Make any revisions, adjust names, fill in bracketed placeholders, or refine clauses below. "
            "All exports will automatically include your latest edits."
        )

        edited_text = st.text_area(
            "Draft Content Editor",
            value=st.session_state["doc_content"],
            height=450,
            key="draft_editor_textarea",
        )

        col_save, col_reset = st.columns([1, 1])
        with col_save:
            if st.button("💾 Save Changes & Update Preview", type="primary", use_container_width=True):
                st.session_state["doc_content"] = edited_text
                st.success("✅ Changes saved! Preview and downloads have been updated.")
                st.rerun()

        with col_reset:
            if st.button("↺ Revert to Original AI Draft", use_container_width=True):
                st.session_state["doc_content"] = st.session_state["original_content"]
                st.info("Reverted to original draft.")
                st.rerun()

    # ---------------------------------------------------------------------
    # TAB 3: EXPORT & DOWNLOAD
    # ---------------------------------------------------------------------
    with tab_export:
        st.markdown("#### 📥 Download Document in Multiple Formats")
        st.caption("Exports use your latest edited draft and include professional formatting, headers, and footers.")

        active_content = st.session_state["doc_content"]
        active_title = st.session_state.get("doc_title", "Legal Document")
        active_type = st.session_state.get("doc_type", "Agreement")
        active_terms = st.session_state.get("terms_raw", "")

        export_payload = {
            "document_title": active_title,
            "document_type": active_type,
            "content": active_content,
            "terms": active_terms,
        }

        col_txt, col_docx, col_pdf = st.columns(3)

        # 1. Plain Text (.txt)
        with col_txt:
            st.markdown("##### 📄 Plain Text (.txt)")
            st.caption("Universal plain text formatted with UTF-8 encoding.")
            try:
                txt_resp = requests.post(
                    f"{BACKEND_URL}/export/txt",
                    json=export_payload,
                    timeout=10,
                )
                if txt_resp.status_code == 200:
                    st.download_button(
                        label="⬇️ Download .TXT",
                        data=txt_resp.content,
                        file_name=f"{active_type.lower().replace(' ', '_')}.txt",
                        mime="text/plain",
                        use_container_width=True,
                    )
                else:
                    st.error("TXT generation error")
            except Exception as e:
                st.error(f"TXT Export error: {e}")

        # 2. Microsoft Word (.docx)
        with col_docx:
            st.markdown("##### 📝 Word Document (.docx)")
            st.caption("Formatted with headings, table of terms, headers, and footers.")
            try:
                docx_resp = requests.post(
                    f"{BACKEND_URL}/export/docx",
                    json=export_payload,
                    timeout=10,
                )
                if docx_resp.status_code == 200:
                    st.download_button(
                        label="⬇️ Download .DOCX",
                        data=docx_resp.content,
                        file_name=f"{active_type.lower().replace(' ', '_')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                    )
                else:
                    st.error("DOCX generation error")
            except Exception as e:
                st.error(f"DOCX Export error: {e}")

        # 3. Branded PDF (.pdf)
        with col_pdf:
            st.markdown("##### 📑 Portable Document (.pdf)")
            st.caption("Clean multi-page PDF layout with headers, footers, and page numbers.")
            try:
                pdf_resp = requests.post(
                    f"{BACKEND_URL}/export/pdf",
                    json=export_payload,
                    timeout=15,
                )
                if pdf_resp.status_code == 200:
                    st.download_button(
                        label="⬇️ Download .PDF",
                        data=pdf_resp.content,
                        file_name=f"{active_type.lower().replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                else:
                    st.error("PDF generation error")
            except Exception as e:
                st.error(f"PDF Export error: {e}")

        st.markdown("---")
        st.info(
            "🔒 **Data Handling Notice:** Your documents are generated in-memory and not stored permanently on public servers."
        )
