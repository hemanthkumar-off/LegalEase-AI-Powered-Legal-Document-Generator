"""Pytest fixtures and test configuration for LegalEase."""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.schemas import DocumentRequest


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    return TestClient(app)


@pytest.fixture
def sample_nda_request():
    """Sample NDA payload matching Scenario 2 in specification."""
    return {
        "document_type": "Non-Disclosure Agreement",
        "parties": "Alpha Technologies (Disclosing Party), Beta Solutions (Receiving Party)",
        "terms": (
            "Confidential information must not be shared; "
            "Information may only be used for project evaluation; "
            "Confidentiality period is 2 years"
        ),
        "effective_date": "October 2, 2026",
        "jurisdiction": "State of California, USA",
        "additional_instructions": "Include injunctive relief clause.",
    }


@pytest.fixture
def sample_employment_request():
    """Sample Employment payload matching Scenario 1 in specification."""
    return {
        "document_type": "Employment Contract",
        "parties": "Apex Innovations Inc. (Employer), Alex Morgan (Employee)",
        "terms": (
            "Position: Senior AI Engineer; "
            "Salary: $135,000 annually; "
            "At-will employment with 14 days notice"
        ),
        "effective_date": "October 15, 2026",
        "jurisdiction": "State of Texas, USA",
    }


@pytest.fixture
def sample_lease_request():
    """Sample Lease payload matching Scenario 3 in specification."""
    return {
        "document_type": "Residential Lease Agreement",
        "parties": "Robert Vance (Landlord), Sarah Jenkins (Tenant)",
        "terms": (
            "Property at 742 Evergreen Terrace; "
            "12 month term; "
            "Monthly rent $2,400 due on 1st of month"
        ),
        "effective_date": "November 1, 2026",
        "jurisdiction": "State of New York, USA",
    }


@pytest.fixture
def mock_generated_draft():
    """Realistic mock legal text returned by Gemini for tests."""
    return (
        "# NON-DISCLOSURE AGREEMENT\n\n"
        "This Non-Disclosure Agreement (the 'Agreement') is entered into as of October 2, 2026 "
        "(the 'Effective Date'), by and between Alpha Technologies ('Disclosing Party') and "
        "Beta Solutions ('Receiving Party').\n\n"
        "## 1. PURPOSE\n"
        "The parties wish to explore a business opportunity concerning project evaluation.\n\n"
        "## 2. CONFIDENTIAL INFORMATION\n"
        "* Confidential information must not be shared with any third parties.\n"
        "* Information may only be used strictly for project evaluation.\n"
        "* Confidentiality obligations remain in effect for 2 years from disclosure.\n\n"
        "## 3. GOVERNING LAW\n"
        "This Agreement shall be governed by the laws of the State of California, USA.\n\n"
        "## 4. SIGNATURES\n"
        "IN WITNESS WHEREOF, the parties hereto have executed this Agreement.\n\n"
        "Alpha Technologies:\n"
        "By: _____________________________\n"
        "Name: [AUTHORIZED SIGNATORY]\n\n"
        "Beta Solutions:\n"
        "By: _____________________________\n"
        "Name: [AUTHORIZED SIGNATORY]\n"
    )
