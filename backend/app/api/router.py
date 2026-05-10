from fastapi import APIRouter

from app.api.admin import router as admin_router
from app.api.chat import router as chat_router
from app.api.graph import router as graph_router
from app.api.health import router as health_router
from app.api.integration import router as integration_router
from app.api.rag import router as rag_router
from app.api.report import router as report_router
from app.api.tasks import router as tasks_router
from app.api.textbooks import router as textbooks_router

api_router = APIRouter()
api_router.include_router(admin_router)
api_router.include_router(health_router)
api_router.include_router(tasks_router)
api_router.include_router(textbooks_router)
api_router.include_router(graph_router)
api_router.include_router(integration_router)
api_router.include_router(rag_router)
api_router.include_router(chat_router)
api_router.include_router(report_router)
