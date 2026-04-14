"""Elasticsearch indexing service."""

import logging
from typing import Optional

from elasticsearch import AsyncElasticsearch

from app.config import settings

logger = logging.getLogger(__name__)

INDEX_NAME = settings.ELASTICSEARCH_INDEX

INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "file_id": {"type": "keyword"},
            "user_id": {"type": "keyword"},
            "filename": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "original_name": {"type": "text"},
            "mime_type": {"type": "keyword"},
            "file_hash": {"type": "keyword"},
            "project_id": {"type": "keyword"},
            "content": {"type": "text", "analyzer": "standard"},
            "indexed_at": {"type": "date"},
        }
    }
}


def get_es_client() -> AsyncElasticsearch:
    """Create and return an Elasticsearch client."""
    return AsyncElasticsearch(settings.ELASTICSEARCH_URL)


async def ensure_index_exists() -> None:
    """Create Elasticsearch index if it doesn't exist."""
    es = get_es_client()
    try:
        exists = await es.indices.exists(index=INDEX_NAME)
        if not exists:
            await es.indices.create(index=INDEX_NAME, body=INDEX_MAPPING)
            logger.info(f"Created Elasticsearch index: {INDEX_NAME}")
    except Exception as e:
        logger.error(f"Failed to create ES index: {e}")
    finally:
        await es.close()


async def index_document(
    file_id: str,
    user_id: str,
    filename: str,
    original_name: str,
    mime_type: str,
    file_hash: str,
    content: str,
    project_id: Optional[str] = None,
) -> bool:
    """Index a document in Elasticsearch."""
    es = get_es_client()
    try:
        from datetime import datetime, timezone
        doc = {
            "file_id": file_id,
            "user_id": user_id,
            "filename": filename,
            "original_name": original_name,
            "mime_type": mime_type,
            "file_hash": file_hash,
            "project_id": project_id,
            "content": content,
            "indexed_at": datetime.now(timezone.utc).isoformat(),
        }
        await es.index(index=INDEX_NAME, id=file_id, document=doc)
        logger.info(f"Indexed document: {file_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to index document {file_id}: {e}")
        return False
    finally:
        await es.close()


async def delete_document(file_id: str) -> bool:
    """Delete a document from Elasticsearch."""
    es = get_es_client()
    try:
        await es.delete(index=INDEX_NAME, id=file_id, ignore=[404])
        logger.info(f"Deleted document: {file_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete document {file_id}: {e}")
        return False
    finally:
        await es.close()
