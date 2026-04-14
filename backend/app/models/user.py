"""User model."""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    """User account model."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="user")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    files: Mapped[list["UploadedFile"]] = relationship("UploadedFile", back_populates="user")
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="user")
    integrations: Mapped[list["Integration"]] = relationship("Integration", back_populates="user")
    monitoring_tasks: Mapped[list["MonitoringTask"]] = relationship("MonitoringTask", back_populates="user")
