from fastapi import FastAPI

from jarvis.api.chat import router as chat_router
from jarvis.api.routes import router
from jarvis.core.config import settings
from jarvis.core.logging import setup_logging
from jarvis.middleware.access import AccessLogMiddleware

setup_logging()


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=settings.debug)
    app.add_middleware(AccessLogMiddleware)
    app.include_router(router)
    app.include_router(chat_router)
    return app


app = create_app()
