"""Governance policy model with versioning."""

from __future__ import annotations

import enum
import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class PolicyCategory(str, enum.Enum):
    """Category of governance policy."""

    DATA_PROTECTION = "data_protection"
    ACCESS_CONTROL = "access_control"
    INCIDENT_RESPONSE = "incident_response"
    COMPLIANCE = "compliance"
    RISK_MANAGEMENT = "risk_management"


class GovernancePolicy(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A versioned governance policy."""

    __tablename__ = "governance_policies"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    category: Mapped[PolicyCategory] = mapped_column(
        Enum(PolicyCategory), nullable=False
    )
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    author_email: Mapped[str] = mapped_column(String(255), nullable=False)
    superseded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("governance_policies.id"),
        nullable=True,
    )

    # Self-referential relationship for version chain
    successor: Mapped["GovernancePolicy | None"] = relationship(
        remote_side="GovernancePolicy.id",
        foreign_keys=[superseded_by],
    )

    def __repr__(self) -> str:
        return f"<GovernancePolicy(title={self.title!r}, v{self.version})>"

    @property
    def is_current(self) -> bool:
        """A policy is current if it hasn't been superseded."""
        return self.superseded_by is None
