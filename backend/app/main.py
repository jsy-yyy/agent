from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.errors import register_error_handlers
from app.services.embedding import create_embedding_provider, IndexService
from app.services.llm import create_llm_provider, LLMService
from app.storage.database import initialize_database


def create_app() -> FastAPI:
    app = FastAPI(title="Knowledge Integration Agent API")
    settings = get_settings()
    initialize_database()
    provider = create_llm_provider()
    app.state.llm_service = LLMService(provider)
    embedding_provider = create_embedding_provider()
    app.state.index_service = IndexService(embedding_provider, dimension=settings.embedding_dimension)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(app)
    app.include_router(api_router)
    return app


app = create_app()
