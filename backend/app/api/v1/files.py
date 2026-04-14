"""File management endpoints."""

import os
import uuid
import hashlib
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.responses import FileResponse

from app.database import get_db
from app.models.user import User
from app.models.file import UploadedFile
from app.schemas.file import FileUploadResponse, FileListResponse, FileMetadata
from app.services.auth import get_current_user
from app.services.antivirus import scan_file
from app.config import settings
from app.tasks.file_tasks import process_uploaded_file

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a file, scan it, and queue for indexing."""
    # Read content
    content = await file.read()

    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    # Scan with ClamAV
    is_clean, message = await scan_file(content)
    if not is_clean:
        raise HTTPException(status_code=400, detail=f"File failed antivirus scan: {message}")

    # Generate storage path
    file_id = str(uuid.uuid4())
    user_dir = Path(settings.UPLOAD_DIR) / str(current_user.id)
    user_dir.mkdir(parents=True, exist_ok=True)
    original_name = file.filename or "unknown"
    stored_filename = f"{file_id}_{original_name}"
    file_path = user_dir / stored_filename

    # Save file
    with open(file_path, "wb") as f:
        f.write(content)

    # Compute hash
    file_hash = hashlib.sha256(content).hexdigest()

    # Save metadata to DB
    db_file = UploadedFile(
        id=file_id,
        user_id=current_user.id,
        filename=stored_filename,
        original_name=original_name,
        size=len(content),
        mime_type=file.content_type or "application/octet-stream",
        file_hash=file_hash,
        file_path=str(file_path),
    )
    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)

    # Queue indexing task
    process_uploaded_file.delay(file_id, str(file_path), file.content_type or "")

    return FileUploadResponse(
        id=db_file.id,
        filename=original_name,
        size=len(content),
        mime_type=db_file.mime_type,
        message="File uploaded successfully and queued for indexing",
    )


@router.get("/list", response_model=FileListResponse)
async def list_files(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all files for current user."""
    result = await db.execute(
        select(UploadedFile).where(UploadedFile.user_id == current_user.id)
    )
    files = result.scalars().all()
    return FileListResponse(files=[FileMetadata.model_validate(f) for f in files])


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a file."""
    result = await db.execute(
        select(UploadedFile).where(
            UploadedFile.id == file_id, UploadedFile.user_id == current_user.id
        )
    )
    db_file = result.scalar_one_or_none()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    # Remove from disk
    if os.path.exists(db_file.file_path):
        os.remove(db_file.file_path)

    await db.delete(db_file)
    await db.commit()


@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download a file."""
    result = await db.execute(
        select(UploadedFile).where(
            UploadedFile.id == file_id, UploadedFile.user_id == current_user.id
        )
    )
    db_file = result.scalar_one_or_none()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    if not os.path.exists(db_file.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=db_file.file_path,
        filename=db_file.original_name,
        media_type=db_file.mime_type,
    )
