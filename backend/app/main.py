from fastapi import FastAPI

from app.api.router import api_router
from app.core.errors import register_error_handlers


def create_app() -> FastAPI:
    app = FastAPI(title="Knowledge Integration Agent API")
    register_error_handlers(app)
    app.include_router(api_router)
    return app


app = create_app()
