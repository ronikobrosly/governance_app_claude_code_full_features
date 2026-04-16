"""Cloud service control model."""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ControlStatus(str, enum.Enum):
    """Lifecycle status of a control."""

    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class Control(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A cloud service control (e.g., encryption-at-rest, MFA enforcement)."""

    __tablename__ = "controls"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ControlStatus] = mapped_column(
        Enum(ControlStatus), default=ControlStatus.DRAFT, nullable=False
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cloud_services.id"),
        nullable=False,
    )
    owner_email: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    service: Mapped["CloudService"] = relationship(back_populates="controls")
    threat_mappings: Mapped[list["ThreatControlMapping"]] = relationship(
        back_populates="control", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Control(name={self.name!r}, status={self.status.value})>"


class CloudService(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A cloud service (e.g., AWS S3, Azure Blob Storage)."""

    __tablename__ = "cloud_services"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    controls: Mapped[list[Control]] = relationship(
        back_populates="service", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<CloudService(name={self.name!r}, provider={self.provider!r})>"
