"""Integration report generation API."""

from fastapi import APIRouter

from app.services.report_service import report_service

router = APIRouter(prefix="/api/report")


@router.post("/generate")
def generate_report() -> dict:
    report_path = report_service.generate()
    return {"status": "generated", "path": str(report_path)}


@router.get("")
def get_report() -> dict:
    content = report_service.read()
    if content is None:
        return {"status": "not_generated", "content": None}
    return {"status": "available", "content": content}
