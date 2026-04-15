"""Integration schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# API key management
# ---------------------------------------------------------------------------

class IntegrationCreate(BaseModel):
    """Schema for creating an integration (legacy, kept for compatibility)."""
    service_name: str
    api_key: str


class IntegrationKeyCreate(BaseModel):
    """Schema for saving an API key for a service."""
    service_name: str
    api_key: str
    api_secret: Optional[str] = None  # used by Censys


class IntegrationKeyResponse(BaseModel):
    """Schema for an integration key response (key is never returned)."""
    id: int
    service_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# Alias for legacy code
IntegrationResponse = IntegrationKeyResponse


# ---------------------------------------------------------------------------
# Query schemas
# ---------------------------------------------------------------------------

class IntegrationQueryRequest(BaseModel):
    """Schema for querying a single OSINT service."""
    service_name: str
    query: str
    query_type: str = "search"  # search | info | scan
    extra_params: Optional[Dict[str, Any]] = None


class IntegrationMultiQueryRequest(BaseModel):
    """Schema for querying multiple OSINT services simultaneously."""
    services: List[str]
    query: str
    query_type: str = "search"
    extra_params: Optional[Dict[str, Any]] = None


class IntegrationQueryResponse(BaseModel):
    """Schema for a single service query response."""
    service_name: str
    results: Optional[Any] = None
    cached: bool = False
    timestamp: str
    credits_used: int = 1
    elapsed_ms: Optional[int] = None
    error: Optional[str] = None


class IntegrationMultiQueryResponse(BaseModel):
    """Schema for multi-service query response."""
    results: Dict[str, IntegrationQueryResponse]
    errors: Dict[str, str]
    total_time_ms: int
    timestamp: str


# ---------------------------------------------------------------------------
# Service info
# ---------------------------------------------------------------------------

class IntegrationServiceInfo(BaseModel):
    """Metadata about a registered OSINT service."""
    name: str
    description: str
    category: str
    supported_query_types: List[str]
    rate_limits: str
    requires_key: bool
    is_configured: bool = False


# ---------------------------------------------------------------------------
# Usage statistics
# ---------------------------------------------------------------------------

class IntegrationUsageStats(BaseModel):
    """Usage statistics for a single service."""
    service_name: str
    queries_today: int = 0
    queries_total: int = 0
    last_query: Optional[datetime] = None
    estimated_credits: int = 0
