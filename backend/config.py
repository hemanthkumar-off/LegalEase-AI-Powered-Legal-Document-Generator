"""Configuration module for LegalEase backend.

Loads configuration from environment variables and .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the repository
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env if present
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)


class Settings:
    """Application settings and configuration."""

    APP_NAME: str = "LegalEase"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-Powered Legal Document Generator"

    # Gemini API Settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    # Default to current standard fast text model; easily configurable via environment
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    GEMINI_TIMEOUT: int = int(os.getenv("GEMINI_TIMEOUT", "60"))
    GEMINI_MAX_RETRIES: int = int(os.getenv("GEMINI_MAX_RETRIES", "3"))

    # Server Settings
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "127.0.0.1")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    BACKEND_URL: str = os.getenv("BACKEND_URL", f"http://{BACKEND_HOST}:{BACKEND_PORT}")

    # Storage Settings
    OUTPUT_DIR: Path = BASE_DIR / "generated"

    # Legal Disclaimer
    LEGAL_DISCLAIMER: str = (
        "LegalEase generates document drafts for informational and educational purposes. "
        "Generated content is not legal advice. Consider consulting a qualified legal professional "
        "for important legal matters."
    )


settings = Settings()

# Ensure output directory exists
settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
