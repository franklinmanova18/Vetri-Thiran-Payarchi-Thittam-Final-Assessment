from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from backend.schemas import (
    DocumentRequest,
    DocumentResponse
)

from services.document_service import DocumentService
from services.export_service import (
    make_docx,
    make_pdf,
    make_txt
)

from utils.text_utils import safe_filename


router = APIRouter(
    prefix="/api",
    tags=["LegalEase"]
)

service = DocumentService()


@router.get("/health")
def health():

    return {
        "status": "ok",
        "service": "LegalEase",
        "demo_mode": service.generator.demo_mode,
        "model": (
            "demo"
            if service.generator.demo_mode
            else service.generator.model
        ),
        "gemini_key_configured": bool(
            service.generator.api_key
        )
    }


@router.post(
    "/generate",
    response_model=DocumentResponse
)
def generate(request: DocumentRequest):

    try:

        result = service.generate(

            document_type=request.document_type,

            parties=request.parties,

            terms=request.terms,

            effective_date=request.effective_date,

            jurisdiction=request.jurisdiction,

            additional_instructions=(
                request.additional_instructions
            ),

            include_disclaimer=(
                request.include_disclaimer
            )
        )

        return DocumentResponse(

            document_type=request.document_type,

            content=result.text,

            model=result.model,

            demo_mode=result.demo_mode
        )

    except RuntimeError as error:

        raise HTTPException(
            status_code=503,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


@router.post("/export/txt")
def export_txt(request: dict):

    content = str(
        request.get("content", "")
    ).strip()

    document_type = str(
        request.get(
            "document_type",
            "Legal Document"
        )
    ).strip()

    if not content:

        raise HTTPException(
            status_code=400,
            detail="Content is required."
        )

    filename = (
        safe_filename(document_type)
        + ".txt"
    )

    return Response(

        content=make_txt(content),

        media_type="text/plain",

        headers={
            "Content-Disposition":
            f'attachment; filename="{filename}"'
        }
    )


@router.post("/export/docx")
def export_docx(request: dict):

    content = str(
        request.get("content", "")
    ).strip()

    document_type = str(
        request.get(
            "document_type",
            "Legal Document"
        )
    ).strip()

    if not content:

        raise HTTPException(
            status_code=400,
            detail="Content is required."
        )

    file_data = make_docx(
        content,
        document_type,
        request.get("logo_base64")
    )

    filename = (
        safe_filename(document_type)
        + ".docx"
    )

    return Response(

        content=file_data,

        media_type=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),

        headers={
            "Content-Disposition":
            f'attachment; filename="{filename}"'
        }
    )


@router.post("/export/pdf")
def export_pdf(request: dict):

    content = str(
        request.get("content", "")
    ).strip()

    document_type = str(
        request.get(
            "document_type",
            "Legal Document"
        )
    ).strip()

    if not content:

        raise HTTPException(
            status_code=400,
            detail="Content is required."
        )

    file_data = make_pdf(
        content,
        document_type,
        request.get("logo_base64")
    )

    filename = (
        safe_filename(document_type)
        + ".pdf"
    )

    return Response(

        content=file_data,

        media_type="application/pdf",

        headers={
            "Content-Disposition":
            f'attachment; filename="{filename}"'
        }
    )