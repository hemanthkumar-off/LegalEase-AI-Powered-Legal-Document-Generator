# LegalEase – AI-Powered Legal Document Generator

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini-4285F4.svg?logo=google&logoColor=white)](https://aistudio.google.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Repository Description:** LegalEase is a Gemini-powered legal document drafting assistant built with FastAPI and Streamlit that generates customizable legal-document drafts with editable previews and TXT, DOCX, and PDF export.

---

## 📌 Project Overview

LegalEase leverages state-of-the-art Generative AI (Google Gemini) to democratize legal document creation. Designed for startup founders, freelancers, property managers, and independent professionals, LegalEase translates conversational inputs (parties, key terms, dates, and jurisdictions) into comprehensive, structured legal draft agreements.

Built with a modular **FastAPI** backend and an intuitive **Streamlit** user interface, the system supports real-time inline editing and multi-format document exporting (.TXT, .DOCX, and .PDF) with professional legal typography, header/footer branding, and page numbering.

---

## ⚖️ Legal Disclaimer

> **IMPORTANT NOTICE:** LegalEase generates document drafts for **informational and educational purposes only**. Generated content does **not** constitute formal legal advice, attorney-client representation, or guaranteed enforceability. Users should consult a licensed legal professional in their governing jurisdiction for sensitive or high-stakes legal matters.

---

## ✨ Key Features

- **Adaptive Document Drafting**: Automatically crafts tailored structures for NDAs, Employment Contracts, Residential Leases, Service Agreements, and Custom Contracts.
- **Strict Anti-Hallucination Controls**: Prompt engineering enforces that the AI never fabricates missing facts (e.g., addresses, dates, compensation amounts). Missing details are preserved with clear placeholders such as `[EMPLOYEE ADDRESS]`.
- **Decoupled Client-Server Architecture**: Streamlit frontend routes all requests through a robust FastAPI REST API.
- **Interactive Document Workspace**:
  - **Formatted Markdown & HTML Preview**: Read drafts with distinct headers, numbered clauses, and bullet points.
  - **Inline Live Text Editor**: Customize clauses, insert names, and refine text with real-time session state synchronization.
  - **Revert to Original Draft**: One-click rollback to the original AI draft.
- **Multi-Format Document Export**:
  - **Plain Text (`.txt`)**: Clean UTF-8 formatted text with legal notices.
  - **Microsoft Word (`.docx`)**: Styled using `python-docx` with 1-inch margins, Times New Roman typography, headers, footers, and structured summary tables for key clauses.
  - **Branded PDF (`.pdf`)**: Generated using `reportlab` with automatic dynamic page numbering (`Page X of Y`), running headers, and clean page wrapping.
- **Preloaded Test Scenarios**: One-click sidebar buttons to populate test cases for Employment Contracts, NDAs, and Residential Leases.

---

## 🏗️ System Architecture

```
                                  ┌────────────────────────┐
                                  │   Streamlit Frontend   │
                                  │    (User Interface)    │
                                  └───────────┬────────────┘
                                              │ HTTP Requests
                                              ▼
                                  ┌────────────────────────┐
                                  │    FastAPI Backend     │
                                  │    (REST API Server)   │
                                  └───────────┬────────────┘
                         ┌────────────────────┼────────────────────┐
                         ▼                    ▼                    ▼
               ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
               │    AI Core       │ │  Document Service│ │  Export Service  │
               │ (Google GenAI)   │ │ (Text Sanitizer) │ │ (TXT, DOCX, PDF) │
               └─────────┬────────┘ └──────────────────┘ └──────────────────┘
                         │
                         ▼
               ┌──────────────────┐
               │  Google Gemini   │
               │  (gemini-2.5-    │
               │      flash)      │
               └──────────────────┘
```

---

## 🛠️ Technology Stack

| Component | Technology | Description |
|---|---|---|
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) | High-performance asynchronous REST API server |
| **API Server** | [Uvicorn](https://www.uvicorn.org/) | Lightning-fast ASGI web server implementation |
| **Data Validation** | [Pydantic v2](https://docs.pydantic.dev/) | Robust payload schema validation & serialization |
| **Frontend Framework** | [Streamlit](https://streamlit.io/) | Interactive, responsive web client |
| **Generative AI SDK** | [Google GenAI SDK](https://github.com/googleapis/python-genai) (`google.genai`) | Official modern Gemini client |
| **Default AI Model** | `gemini-2.5-flash` | Fast, cost-efficient multimodal text generation |
| **Word Processing** | [python-docx](https://python-docx.readthedocs.io/) | Microsoft Word (.docx) generation with styles |
| **PDF Generation** | [ReportLab](https://www.reportlab.com/) | Industrial-strength PDF layout with headers & footers |
| **Testing** | [Pytest](https://docs.pytest.org/) | Comprehensive test suite with mocked AI responses |

---

## 📂 Project Structure

```
LegalEase/
├── backend/
│   ├── __init__.py               # Backend package initializer
│   ├── config.py                 # Configuration & environment variable settings
│   ├── main.py                   # FastAPI application initialization & CORS
│   ├── routes.py                 # REST API endpoints (health, generate, exports)
│   ├── schemas.py                # Pydantic request/response data models
│   ├── ai_core/
│   │   ├── __init__.py           # AI Core package initializer
│   │   └── gemini_generator.py   # Official Google GenAI SDK client & prompts
│   ├── services/
│   │   ├── __init__.py           # Services package initializer
│   │   ├── document_service.py   # Generation workflow orchestration
│   │   └── export_service.py     # TXT, DOCX (python-docx), and PDF (ReportLab) generators
│   └── utils/
│       ├── __init__.py           # Utilities package initializer
│       └── text_utils.py         # Smart quote normalization, parsing & filename helpers
│
├── frontend/
│   ├── app.py                    # Streamlit web application
│   └── assets/
│       └── logo.png              # LegalEase brand identity mark
│
├── tests/
│   ├── __init__.py               # Test package initializer
│   ├── conftest.py               # Test fixtures and mock data
│   ├── test_routes.py            # API route tests (status, health, validation)
│   ├── test_gemini.py            # AI Core unit tests & prompt verification
│   ├── test_exporters.py         # TXT, DOCX, and PDF file integrity tests
│   ├── test_sanitization.py      # Filename & text normalization tests
│   └── test_live_gemini.py       # Optional live API verification test
│
├── .env.example                  # Environment template for API keys and configuration
├── .gitignore                    # Git exclusion rules (keys, caches, exports)
├── requirements.txt              # Pinned production and test dependencies
├── checklist.md                  # Project implementation and verification checklist
└── README.md                     # Comprehensive project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10 or higher
- Git
- Google Gemini API Key (Obtain free from [Google AI Studio](https://aistudio.google.com/app/apikey))

### 2. Clone Repository
```bash
git clone https://github.com/your-username/legalease.git
cd legalease
```

### 3. Create Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy `.env.example` to `.env` and insert your Gemini API Key:
```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux / macOS
cp .env.example .env
```

Open `.env` in any text editor and supply your key:
```env
GEMINI_API_KEY=AIzaSyYourActualApiKeyHere
GEMINI_MODEL=gemini-2.5-flash
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
BACKEND_URL=http://127.0.0.1:8000
```

---

## 🖥️ Running the Application

### Option 1: One-Command Runner (Recommended)
You can launch both the FastAPI backend and Streamlit frontend simultaneously with a single command:
```bash
python run.py
```
This launcher:
- Boots the FastAPI server on port 8000
- Polls until the backend is healthy
- Boots the Streamlit UI on port 8501
- Automatically opens your web browser to `http://localhost:8501`
- Shuts down both servers cleanly on `Ctrl+C`

### Option 2: Running Services Separately

#### Step 1: Start FastAPI Backend
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
- API Documentation (Swagger UI): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- API Health Status: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

#### Step 2: Start Streamlit Frontend
In a new terminal window:
```bash
streamlit run frontend/app.py
```
- Application Web UI: [http://localhost:8501](http://localhost:8501)

---

## ⚡ Offline & Demo Mode (Runs Without API Key)
LegalEase is built with resilience in mind. If you do not have a Gemini API key or if the Gemini API is unreachable, the system **automatically activates the LegalEase Built-in Legal Drafting Engine**. It dynamically constructs full-length, professional legal agreements incorporating all of your parties, clauses, dates, and jurisdictions—allowing complete testing of document generation, live inline editing, and TXT/DOCX/PDF downloads without any blockers. When a valid Google Gemini key is placed in `.env`, the system automatically switches to live Gemini AI.

---

## 🧪 Testing

LegalEase includes an extensive test suite covering all API endpoints, input validation, Gemini error handling, text sanitization, and file generation integrity.

Run the automated test suite (all tests mock Gemini to conserve API quota):
```bash
pytest -v
```

### Run Optional Live Gemini Verification Test
To run the live test against Google's live Gemini API:
```bash
$env:RUN_LIVE_GEMINI_TEST="1"; pytest tests/test_live_gemini.py -v -s
```

---

## 📑 Supported Document Types

1. **Employment Contract**: Roles, responsibilities, compensation, benefits, at-will status, IP assignment, and confidentiality.
2. **Non-Disclosure Agreement (NDA)**: Unilateral or mutual confidentiality, scope of proprietary information, term duration, and return/destruction mandates.
3. **Residential Lease Agreement**: Premises description, lease duration, monthly rent, security deposits, utilities, and occupancy rules.
4. **Freelance / Independent Contractor Agreement**: Deliverables, milestone payments, independent status, and copyright transfer.
5. **General Commercial Contract**: Core agreements, warranties, liability limitations, and indemnification.
6. **Business Agreement**: Corporate partnerships, profit/loss sharing, and governance.
7. **Employment Offer Letter**: Formal offer terms, starting salary, reporting manager, and contingencies.
8. **Other / Custom Document**: User-defined custom contract types.

---

## 🔒 Security & Privacy

- **Zero Secret Leakage**: API keys are loaded via environment variables and excluded from source control through `.gitignore`.
- **In-Memory Document Generation**: User drafts and exports are streamed in-memory without persistent logging of sensitive legal text.
- **Sanitized Filenames**: Output filenames are strictly sanitized to prevent directory traversal or filesystem vulnerabilities.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
