"""Monitoring task endpoints (stub)."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.monitoring import MonitoringTask
from app.schemas.monitoring import MonitoringTaskCreate, MonitoringTaskResponse
from app.services.auth import get_current_user

router = APIRouter()


@router.get("", response_model=List[MonitoringTaskResponse])
async def list_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List monitoring tasks for current user."""
    result = await db.execute(
        select(MonitoringTask).where(MonitoringTask.user_id == current_user.id)
    )
    tasks = result.scalars().all()
    return [MonitoringTaskResponse.model_validate(t) for t in tasks]


@router.post("", response_model=MonitoringTaskResponse, status_code=201)
async def create_task(
    data: MonitoringTaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a monitoring task."""
    task = MonitoringTask(
        user_id=current_user.id,
        task_type=data.task_type,
        config_json=data.config_json,
        schedule=data.schedule,
        is_active=True,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return MonitoringTaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a monitoring task."""
    result = await db.execute(
        select(MonitoringTask).where(
            MonitoringTask.id == task_id, MonitoringTask.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
    await db.commit()
