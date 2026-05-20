from fastapi import FastAPI

from jarvis.api.routes import router
from jarvis.core.config import settings
from jarvis.core.logging import setup_logging
from jarvis.middleware.access import AccessLogMiddleware

setup_logging()


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=settings.debug)
    app.add_middleware(AccessLogMiddleware)
    app.include_router(router)
    return app


app = create_app()
