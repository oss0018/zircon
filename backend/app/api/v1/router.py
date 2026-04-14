"""Main v1 API router."""

from fastapi import APIRouter

from app.api.v1 import auth, files, search, integrations, monitoring, brand

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(files.router, prefix="/files", tags=["Files"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["Integrations"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["Monitoring"])
api_router.include_router(brand.router, prefix="/brand", tags=["Brand Protection"])
