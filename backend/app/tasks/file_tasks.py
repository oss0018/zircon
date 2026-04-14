"""File processing Celery tasks."""

import asyncio
import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.file_tasks.process_uploaded_file", bind=True, max_retries=3)
def process_uploaded_file(self, file_id: str, file_path: str, mime_type: str):
    """
    Process an uploaded file: extract content and index in Elasticsearch.
    """
    try:
        asyncio.run(_process_file(file_id, file_path, mime_type))
    except Exception as exc:
        logger.error(f"Failed to process file {file_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)


async def _process_file(file_id: str, file_path: str, mime_type: str):
    """Async file processing logic."""
    from app.services.file_processor import extract_text_from_file
    from app.services.indexer import index_document, ensure_index_exists
    from app.models.file import UploadedFile
    from sqlalchemy import select

    logger.info(f"Processing file {file_id}: {file_path}")

    # Extract text content
    content = extract_text_from_file(file_path, mime_type)
    if not content:
        logger.warning(f"Could not extract content from {file_path}")
        content = ""

    # Get file metadata from DB
    from app.database import get_session_factory
    async with get_session_factory()() as db:
        result = await db.execute(select(UploadedFile).where(UploadedFile.id == file_id))
        db_file = result.scalar_one_or_none()

        if not db_file:
            logger.error(f"File {file_id} not found in DB")
            return

        # Ensure ES index exists
        await ensure_index_exists()

        # Index in Elasticsearch
        success = await index_document(
            file_id=file_id,
            user_id=str(db_file.user_id),
            filename=db_file.filename,
            original_name=db_file.original_name,
            mime_type=db_file.mime_type,
            file_hash=db_file.file_hash,
            content=content,
            project_id=str(db_file.project_id) if db_file.project_id else None,
        )

        if success:
            db_file.indexed = True
            await db.commit()
            logger.info(f"Successfully indexed file {file_id}")
