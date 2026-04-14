"""File schemas."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class FileMetadata(BaseModel):
    """File metadata schema."""
    id: str
    filename: str
    original_name: str
    size: int
    mime_type: str
    file_hash: str
    indexed: bool
    project_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class FileUploadResponse(BaseModel):
    """Response after file upload."""
    id: str
    filename: str
    size: int
    mime_type: str
    message: str


class FileListResponse(BaseModel):
    """Response for file list."""
    files: List[FileMetadata]
    total: int = 0

    def model_post_init(self, __context):
        self.total = len(self.files)
