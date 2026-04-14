"""Monitoring schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class MonitoringTaskCreate(BaseModel):
    """Schema for creating a monitoring task."""
    task_type: str
    config_json: Optional[str] = None
    schedule: Optional[str] = None


class MonitoringTaskResponse(BaseModel):
    """Schema for monitoring task response."""
    id: int
    task_type: str
    config_json: Optional[str] = None
    schedule: Optional[str] = None
    is_active: bool
    last_run: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}
