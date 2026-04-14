"""OSINT integrations endpoints (stub)."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.integration import Integration
from app.schemas.integration import IntegrationCreate, IntegrationResponse
from app.services.auth import get_current_user
from app.services.encryption import encrypt_value, decrypt_value

router = APIRouter()


@router.get("", response_model=List[IntegrationResponse])
async def list_integrations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all integrations for current user."""
    result = await db.execute(
        select(Integration).where(Integration.user_id == current_user.id)
    )
    integrations = result.scalars().all()
    return [IntegrationResponse.model_validate(i) for i in integrations]


@router.post("", response_model=IntegrationResponse, status_code=201)
async def create_integration(
    data: IntegrationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new OSINT integration with an API key."""
    encrypted_key = encrypt_value(data.api_key)
    integration = Integration(
        user_id=current_user.id,
        service_name=data.service_name,
        encrypted_api_key=encrypted_key,
        is_active=True,
    )
    db.add(integration)
    await db.commit()
    await db.refresh(integration)
    return IntegrationResponse.model_validate(integration)


@router.delete("/{integration_id}", status_code=204)
async def delete_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an integration."""
    result = await db.execute(
        select(Integration).where(
            Integration.id == integration_id, Integration.user_id == current_user.id
        )
    )
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    await db.delete(integration)
    await db.commit()


@router.post("/{integration_id}/query")
async def trigger_osint_query(
    integration_id: int,
    query: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger an OSINT query via the specified integration (stub)."""
    result = await db.execute(
        select(Integration).where(
            Integration.id == integration_id, Integration.user_id == current_user.id
        )
    )
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    # Stub: return placeholder data
    return {
        "integration": integration.service_name,
        "query": query,
        "status": "stub",
        "results": [],
        "message": "Full integration logic will be implemented in Phase 2",
    }
