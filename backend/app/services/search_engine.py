"""Elasticsearch search service."""

import logging
from datetime import date
from typing import Optional

from elasticsearch import AsyncElasticsearch

from app.config import settings
from app.schemas.search import SearchResponse, SearchHit

logger = logging.getLogger(__name__)


async def search_documents(
    query: str,
    file_type: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    project_id: Optional[str] = None,
    operator: str = "AND",
    page: int = 1,
    page_size: int = 20,
) -> SearchResponse:
    """Search documents in Elasticsearch."""
    es = AsyncElasticsearch(settings.ELASTICSEARCH_URL)

    try:
        must_clauses = [
            {
                "query_string": {
                    "query": query,
                    "fields": ["content", "filename", "original_name"],
                    "default_operator": operator,
                }
            }
        ]

        filter_clauses = []

        if file_type:
            filter_clauses.append({"term": {"mime_type": file_type}})

        if date_from or date_to:
            date_range = {}
            if date_from:
                date_range["gte"] = date_from.isoformat()
            if date_to:
                date_range["lte"] = date_to.isoformat()
            filter_clauses.append({"range": {"indexed_at": date_range}})

        if project_id:
            filter_clauses.append({"term": {"project_id": project_id}})

        es_query = {
            "bool": {
                "must": must_clauses,
                "filter": filter_clauses,
            }
        }

        from_offset = (page - 1) * page_size

        response = await es.search(
            index=settings.ELASTICSEARCH_INDEX,
            query=es_query,
            highlight={
                "fields": {"content": {}, "filename": {}},
                "pre_tags": ["<mark>"],
                "post_tags": ["</mark>"],
                "fragment_size": 200,
            },
            from_=from_offset,
            size=page_size,
        )

        hits = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            highlights = []
            if "highlight" in hit:
                for field_highlights in hit["highlight"].values():
                    highlights.extend(field_highlights)

            hits.append(
                SearchHit(
                    file_id=source.get("file_id", hit["_id"]),
                    filename=source.get("original_name", source.get("filename", "")),
                    score=hit["_score"],
                    highlights=highlights,
                    metadata={
                        "mime_type": source.get("mime_type"),
                        "project_id": source.get("project_id"),
                        "indexed_at": source.get("indexed_at"),
                    },
                )
            )

        total = response["hits"]["total"]["value"] if isinstance(response["hits"]["total"], dict) else response["hits"]["total"]

        return SearchResponse(
            query=query,
            total=total,
            hits=hits,
            page=page,
            page_size=page_size,
        )

    except Exception as e:
        logger.error(f"Search failed: {e}")
        return SearchResponse(query=query, total=0, hits=[], page=page, page_size=page_size)
    finally:
        await es.close()
