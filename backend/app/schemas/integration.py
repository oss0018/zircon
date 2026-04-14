"""Integration schemas."""

from datetime import datetime
from pydantic import BaseModel


class IntegrationCreate(BaseModel):
    """Schema for creating an integration."""
    service_name: str
    api_key: str


class IntegrationResponse(BaseModel):
    """Schema for integration response."""
    id: int
    service_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
