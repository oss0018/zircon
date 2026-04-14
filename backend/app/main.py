"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.responses import JSONResponse

from app.config import settings
from app.api.v1.router import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Zircon FRT backend...")
    yield
    logger.info("Shutting down Zircon FRT backend...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url=None,
    redoc_url=None,
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/api/docs", include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(openapi_url="/api/openapi.json", title=f"{settings.APP_NAME} - Swagger UI")


@app.get("/api/redoc", include_in_schema=False)
async def custom_redoc():
    return get_redoc_html(openapi_url="/api/openapi.json", title=f"{settings.APP_NAME} - ReDoc")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse({"status": "ok", "version": settings.APP_VERSION})
