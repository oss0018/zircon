"""Search schemas."""

from datetime import date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class SearchRequest(BaseModel):
    """Search request schema."""
    query: str
    file_type: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    project_id: Optional[str] = None
    operator: str = "AND"
    page: int = 1
    page_size: int = 20


class SearchHit(BaseModel):
    """A single search result."""
    file_id: str
    filename: str
    score: float
    highlights: List[str] = []
    metadata: Dict[str, Any] = {}


class SearchResponse(BaseModel):
    """Search response schema."""
    query: str
    total: int
    hits: List[SearchHit]
    page: int
    page_size: int
