"""FastAPI application factory."""

from fastapi import FastAPI

from src.api.controls import router as controls_router
from src.utils.config import settings
from src.utils.logging import setup_logging


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    setup_logging(settings.log_level)

    app = FastAPI(
        title="CloudGov Platform API",
        version="1.0.0",
        docs_url="/docs",
    )

    app.include_router(controls_router, prefix="/api/v1")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
