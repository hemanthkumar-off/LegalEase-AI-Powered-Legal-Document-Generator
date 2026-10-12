"""FastAPI route definitions for LegalEase."""

import logging
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.schemas import (
    DocumentRequest,
    DocumentResponse,
    ExportRequest,
    HealthResponse,
)
from backend.services.document_service import DocumentService
from backend.services.export_service import ExportService
from backend.ai_core.gemini_generator import GeminiServiceError
from backend.utils.text_utils import sanitize_filename

logger = logging.getLogger("LegalEase.Routes")

router = APIRouter()
doc_service = DocumentService()


@router.get("/", summary="Root status check")
async def root():
    """Verify backend service is running."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "description": settings.APP_DESCRIPTION,
        "endpoints": {
            "health": "/health",
            "generate": "/generate (POST)",
            "export_txt": "/export/txt (POST)",
            "export_docx": "/export/docx (POST)",
            "export_pdf": "/export/pdf (POST)",
            "docs": "/docs",
        },
    }


@router.get("/health", response_model=HealthResponse, summary="Health status check")
async def health():
    """Return application and AI service configuration health."""
    has_key = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip())
    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        gemini_configured=has_key,
        gemini_model=settings.GEMINI_MODEL,
    )


@router.post("/generate", response_model=DocumentResponse, summary="Generate legal document")
async def generate_document(request: DocumentRequest):
    """Generate a structured legal document draft using Google Gemini."""
    try:
        response = doc_service.generate_draft(request)
        return response
    except GeminiServiceError as e:
        logger.error(f"Gemini service error: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.exception("Unexpected error in /generate")
        raise HTTPException(
            status_code=500,
            detail="Document generation is temporarily unavailable. Please try again.",
        )


@router.post("/export/txt", summary="Export document to TXT")
async def export_txt(request: ExportRequest):
    """Generate and return a plain text file."""
    try:
        txt_bytes = ExportService.generate_txt(
            content=request.content,
            document_title=request.document_title,
            document_type=request.document_type,
        )
        filename = sanitize_filename(request.document_title or request.document_type, "txt")
        return Response(
            content=txt_bytes,
            media_type="text/plain; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        logger.exception("Export TXT failed")
        raise HTTPException(status_code=500, detail=f"Failed to generate TXT: {str(e)}")


@router.post("/export/docx", summary="Export document to DOCX")
async def export_docx(request: ExportRequest):
    """Generate and return a styled Microsoft Word (.docx) document."""
    try:
        docx_bytes = ExportService.generate_docx(
            content=request.content,
            document_title=request.document_title,
            document_type=request.document_type,
            terms=request.terms,
        )
        filename = sanitize_filename(request.document_title or request.document_type, "docx")
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        logger.exception("Export DOCX failed")
        raise HTTPException(status_code=500, detail=f"Failed to generate DOCX: {str(e)}")


@router.post("/export/pdf", summary="Export document to PDF")
async def export_pdf(request: ExportRequest):
    """Generate and return a branded PDF document."""
    try:
        pdf_bytes = ExportService.generate_pdf(
            content=request.content,
            document_title=request.document_title,
            document_type=request.document_type,
        )
        filename = sanitize_filename(request.document_title or request.document_type, "pdf")
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        logger.exception("Export PDF failed")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")
