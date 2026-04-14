"""Search endpoints."""

from fastapi import APIRouter, Depends

from app.models.user import User
from app.schemas.search import SearchRequest, SearchResponse
from app.services.auth import get_current_user
from app.services.search_engine import search_documents

router = APIRouter()


@router.post("", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    current_user: User = Depends(get_current_user),
):
    """Full-text search in Elasticsearch."""
    results = await search_documents(
        query=request.query,
        file_type=request.file_type,
        date_from=request.date_from,
        date_to=request.date_to,
        project_id=request.project_id,
        operator=request.operator,
    )
    return results
