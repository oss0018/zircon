"""Celery tasks for OSINT integration queries."""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Run an async coroutine in a new event loop (used inside Celery tasks)."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="app.tasks.integration_tasks.run_integration_query", bind=True, max_retries=3)
def run_integration_query(
    self,
    user_id: str,
    service_name: str,
    query: str,
    query_type: str = "search",
    extra_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Execute a single integration query asynchronously via Celery."""
    from app.database import AsyncSessionLocal
    from app.services import integration_service

    async def _execute():
        async with AsyncSessionLocal()() as db:
            return await integration_service.execute_query(
                db=db,
                user_id=user_id,
                service_name=service_name,
                query=query,
                query_type=query_type,
                extra_params=extra_params or {},
            )

    try:
        return _run_async(_execute())
    except Exception as exc:
        logger.error(f"run_integration_query failed: {exc}")
        raise self.retry(exc=exc, countdown=10)


@celery_app.task(name="app.tasks.integration_tasks.run_multi_integration_query", bind=True, max_retries=3)
def run_multi_integration_query(
    self,
    user_id: str,
    service_names: List[str],
    query: str,
    query_type: str = "search",
    extra_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Execute queries across multiple services in parallel via Celery."""
    from app.database import AsyncSessionLocal
    from app.services import integration_service

    async def _execute():
        async with AsyncSessionLocal()() as db:
            return await integration_service.execute_multi_query(
                db=db,
                user_id=user_id,
                service_names=service_names,
                query=query,
                query_type=query_type,
                extra_params=extra_params or {},
            )

    try:
        return _run_async(_execute())
    except Exception as exc:
        logger.error(f"run_multi_integration_query failed: {exc}")
        raise self.retry(exc=exc, countdown=10)


@celery_app.task(name="app.tasks.integration_tasks.check_integration_health")
def check_integration_health() -> Dict[str, Any]:
    """Periodically verify that stored API keys are valid by performing lightweight checks."""
    from app.database import AsyncSessionLocal
    from sqlalchemy import select
    from app.models.integration import Integration
    from app.services.encryption import decrypt_value
    from app.integrations import IntegrationRegistry

    async def _check():
        results: Dict[str, Any] = {}
        async with AsyncSessionLocal()() as db:
            result = await db.execute(select(Integration).where(Integration.is_active.is_(True)))
            integrations = result.scalars().all()
            for integration in integrations:
                key = f"{integration.user_id}:{integration.service_name}"
                try:
                    api_key = decrypt_value(integration.encrypted_api_key)
                    instance = IntegrationRegistry.create_instance(
                        integration.service_name, api_key=api_key
                    )
                    # Perform a lightweight search to test connectivity
                    test_result = await instance.search("test")
                    results[key] = {
                        "status": "ok" if "error" not in test_result else "error",
                        "service": integration.service_name,
                    }
                except Exception as exc:
                    results[key] = {"status": "error", "error": str(exc)}
        return results

    return _run_async(_check())
