"""Threat registry model."""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ThreatSeverity(str, enum.Enum):
    """Severity classification for threats."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Threat(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A threat in the threat registry (e.g., data exfiltration, DDoS)."""

    __tablename__ = "threats"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[ThreatSeverity] = mapped_column(
        Enum(ThreatSeverity), nullable=False
    )
    mitre_attack_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    likelihood: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    # Relationships
    control_mappings: Mapped[list["ThreatControlMapping"]] = relationship(
        back_populates="threat", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Threat(name={self.name!r}, severity={self.severity.value})>"


class ThreatControlMapping(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Links threats to the controls that mitigate them."""

    __tablename__ = "threat_control_mappings"

    threat_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("threats.id"), nullable=False
    )
    control_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("controls.id"), nullable=False
    )
    effectiveness: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.5
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    threat: Mapped[Threat] = relationship(back_populates="control_mappings")
    control: Mapped["Control"] = relationship(back_populates="threat_mappings")

    def __repr__(self) -> str:
        return f"<ThreatControlMapping(threat={self.threat_id}, control={self.control_id})>"
