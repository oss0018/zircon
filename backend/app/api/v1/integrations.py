"""OSINT integrations API endpoints."""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.integration import Integration
from app.models.user import User
from app.schemas.integration import (
    IntegrationKeyCreate,
    IntegrationKeyResponse,
    IntegrationMultiQueryRequest,
    IntegrationMultiQueryResponse,
    IntegrationQueryRequest,
    IntegrationQueryResponse,
    IntegrationServiceInfo,
    IntegrationUsageStats,
)
from app.services.auth import get_current_user
from app.services.encryption import encrypt_value
from app.services import integration_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Key management
# ---------------------------------------------------------------------------

@router.post("/keys", response_model=IntegrationKeyResponse, status_code=201)
async def save_api_key(
    data: IntegrationKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save an encrypted API key for an OSINT service."""
    # If a record already exists for this user+service, update it
    result = await db.execute(
        select(Integration).where(
            Integration.user_id == current_user.id,
            Integration.service_name == data.service_name,
        )
    )
    existing = result.scalar_one_or_none()

    encrypted_key = encrypt_value(data.api_key)

    if existing:
        existing.encrypted_api_key = encrypted_key
        existing.is_active = True
        await db.commit()
        await db.refresh(existing)
        return IntegrationKeyResponse.model_validate(existing)

    integration = Integration(
        user_id=current_user.id,
        service_name=data.service_name,
        encrypted_api_key=encrypted_key,
        is_active=True,
    )
    db.add(integration)
    await db.commit()
    await db.refresh(integration)
    return IntegrationKeyResponse.model_validate(integration)


@router.get("/keys", response_model=List[IntegrationKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all configured integrations for the current user (without keys)."""
    result = await db.execute(
        select(Integration).where(Integration.user_id == current_user.id)
    )
    integrations = result.scalars().all()
    return [IntegrationKeyResponse.model_validate(i) for i in integrations]


@router.delete("/keys/{service_name}", status_code=204)
async def remove_api_key(
    service_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove the API key for a specific service."""
    result = await db.execute(
        select(Integration).where(
            Integration.user_id == current_user.id,
            Integration.service_name == service_name,
        )
    )
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    await db.delete(integration)
    await db.commit()


# ---------------------------------------------------------------------------
# Legacy endpoints (kept for backwards compatibility)
# ---------------------------------------------------------------------------

@router.get("", response_model=List[IntegrationKeyResponse])
async def list_integrations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all integrations for current user (legacy endpoint)."""
    return await list_api_keys(current_user=current_user, db=db)


@router.post("", response_model=IntegrationKeyResponse, status_code=201)
async def create_integration(
    data: IntegrationKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new OSINT integration (legacy endpoint)."""
    return await save_api_key(data=data, current_user=current_user, db=db)


@router.delete("/{integration_id}", status_code=204)
async def delete_integration_by_id(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an integration by ID (legacy endpoint)."""
    result = await db.execute(
        select(Integration).where(
            Integration.id == integration_id,
            Integration.user_id == current_user.id,
        )
    )
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    await db.delete(integration)
    await db.commit()


# ---------------------------------------------------------------------------
# Query endpoints
# ---------------------------------------------------------------------------

@router.post("/query", response_model=IntegrationQueryResponse)
async def query_service(
    request: IntegrationQueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Query a specific OSINT service."""
    response = await integration_service.execute_query(
        db=db,
        user_id=current_user.id,
        service_name=request.service_name,
        query=request.query,
        query_type=request.query_type,
        extra_params=request.extra_params,
    )
    return IntegrationQueryResponse(**response)


@router.post("/query/multi", response_model=IntegrationMultiQueryResponse)
async def query_multiple_services(
    request: IntegrationMultiQueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Query multiple OSINT services simultaneously."""
    response = await integration_service.execute_multi_query(
        db=db,
        user_id=current_user.id,
        service_names=request.services,
        query=request.query,
        query_type=request.query_type,
        extra_params=request.extra_params,
    )
    # Convert per-service results to IntegrationQueryResponse objects
    results = {
        svc: IntegrationQueryResponse(**data)
        for svc, data in response["results"].items()
    }
    return IntegrationMultiQueryResponse(
        results=results,
        errors=response["errors"],
        total_time_ms=response["total_time_ms"],
        timestamp=response["timestamp"],
    )


# ---------------------------------------------------------------------------
# Discovery & usage
# ---------------------------------------------------------------------------

@router.get("/services", response_model=List[IntegrationServiceInfo])
async def list_services(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all available OSINT services with descriptions."""
    # Get configured services for this user
    result = await db.execute(
        select(Integration.service_name).where(
            Integration.user_id == current_user.id,
            Integration.is_active.is_(True),
        )
    )
    configured = {row[0] for row in result.fetchall()}

    services = integration_service.list_services()
    return [
        IntegrationServiceInfo(
            is_configured=svc["name"] in configured,
            **{k: v for k, v in svc.items() if k != "is_configured"},
        )
        for svc in services
    ]


@router.get("/usage", response_model=List[IntegrationUsageStats])
async def get_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get API usage stats per service (stub — real tracking requires a usage table)."""
    result = await db.execute(
        select(Integration).where(
            Integration.user_id == current_user.id,
            Integration.is_active.is_(True),
        )
    )
    integrations = result.scalars().all()
    return [
        IntegrationUsageStats(
            service_name=i.service_name,
            queries_today=0,
            queries_total=0,
            last_query=None,
            estimated_credits=0,
        )
        for i in integrations
    ]
