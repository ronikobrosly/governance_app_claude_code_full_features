"""Risk score computation service.

Risk scores are COMPUTED, never stored. This ensures scores always
reflect the current state of threats, controls, and their mappings.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.control import Control, ControlStatus
from src.models.threat import Threat, ThreatControlMapping
from src.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class RiskScore:
    """Computed risk score for a threat."""

    threat_id: uuid.UUID
    threat_name: str
    raw_score: float
    mitigated_score: float
    active_controls_count: int
    coverage_ratio: float

    @property
    def risk_level(self) -> str:
        """Classify the mitigated score into a human-readable level."""
        if self.mitigated_score >= 0.75:
            return "critical"
        if self.mitigated_score >= 0.5:
            return "high"
        if self.mitigated_score >= 0.25:
            return "medium"
        return "low"


async def compute_risk_score(
    session: AsyncSession, threat_id: uuid.UUID
) -> RiskScore:
    """Compute the risk score for a single threat.

    Formula:
        raw_score = severity_weight * likelihood
        mitigation_factor = sum(mapping.effectiveness) for active controls
        mitigated_score = raw_score * max(0, 1 - mitigation_factor)
    """
    logger.info("computing_risk_score", threat_id=str(threat_id))

    result = await session.execute(
        select(Threat)
        .options(
            selectinload(Threat.control_mappings).selectinload(
                ThreatControlMapping.control
            )
        )
        .where(Threat.id == threat_id)
    )
    threat = result.scalar_one_or_none()
    if threat is None:
        from src.utils.exceptions import NotFoundError

        raise NotFoundError("Threat", str(threat_id))

    severity_weights = {"low": 0.25, "medium": 0.5, "high": 0.75, "critical": 1.0}
    raw_score = severity_weights[threat.severity.value] * threat.likelihood

    active_mappings = [
        m
        for m in threat.control_mappings
        if m.control.status == ControlStatus.ACTIVE
    ]
    mitigation_factor = sum(m.effectiveness for m in active_mappings)
    mitigated_score = raw_score * max(0.0, 1.0 - mitigation_factor)
    total_mappings = len(threat.control_mappings)
    coverage = len(active_mappings) / total_mappings if total_mappings > 0 else 0.0

    score = RiskScore(
        threat_id=threat.id,
        threat_name=threat.name,
        raw_score=round(raw_score, 4),
        mitigated_score=round(mitigated_score, 4),
        active_controls_count=len(active_mappings),
        coverage_ratio=round(coverage, 4),
    )
    logger.info(
        "risk_score_computed",
        threat_id=str(threat_id),
        mitigated_score=score.mitigated_score,
        risk_level=score.risk_level,
    )
    return score
