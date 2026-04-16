"""Shared test fixtures for the CloudGov platform."""

from __future__ import annotations

import uuid
from datetime import date

import pytest

from src.models.control import CloudService, Control, ControlStatus
from src.models.governance import GovernancePolicy, PolicyCategory
from src.models.threat import Threat, ThreatControlMapping, ThreatSeverity


@pytest.fixture
def sample_service_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def sample_service(sample_service_id: uuid.UUID) -> CloudService:
    return CloudService(
        id=sample_service_id,
        name="AWS S3",
        provider="aws",
        description="Object storage service",
    )


@pytest.fixture
def sample_control(sample_service_id: uuid.UUID) -> Control:
    return Control(
        id=uuid.uuid4(),
        name="Encryption at Rest",
        description="All data must be encrypted at rest using AES-256",
        status=ControlStatus.ACTIVE,
        category="data_protection",
        service_id=sample_service_id,
        owner_email="security@example.com",
    )


@pytest.fixture
def sample_threat() -> Threat:
    return Threat(
        id=uuid.uuid4(),
        name="Data Exfiltration",
        description="Unauthorized data transfer to external systems",
        severity=ThreatSeverity.HIGH,
        mitre_attack_id="T1567",
        likelihood=0.7,
    )


@pytest.fixture
def sample_policy() -> GovernancePolicy:
    return GovernancePolicy(
        id=uuid.uuid4(),
        title="Data Retention Policy",
        body="All customer data must be retained for 7 years...",
        version=1,
        category=PolicyCategory.DATA_PROTECTION,
        effective_date=date(2024, 1, 1),
        author_email="compliance@example.com",
    )


@pytest.fixture
def sample_threat_control_mapping(
    sample_threat: Threat, sample_control: Control
) -> ThreatControlMapping:
    return ThreatControlMapping(
        id=uuid.uuid4(),
        threat_id=sample_threat.id,
        control_id=sample_control.id,
        effectiveness=0.8,
        notes="Encryption significantly reduces exfiltration risk",
    )
