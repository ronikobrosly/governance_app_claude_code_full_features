"""Unit tests for the threat feed ETL pipeline."""

from __future__ import annotations

import pytest

from src.etl.threat_feed_pipeline import ThreatFeedPipeline, ThreatFeedRecord


@pytest.mark.asyncio
async def test_pipeline_extract_returns_data() -> None:
    """Extract step returns a list of raw records."""
    pipeline = ThreatFeedPipeline(name="threat_feed")
    raw = await pipeline.extract()
    assert len(raw) > 0
    assert all("name" in r for r in raw)


@pytest.mark.asyncio
async def test_pipeline_validate_accepts_valid_record() -> None:
    """Valid records pass validation."""
    pipeline = ThreatFeedPipeline(name="threat_feed")
    record = {
        "external_id": "TF-001",
        "name": "Test Threat",
        "description": "A test threat",
        "severity": "high",
        "likelihood": 0.5,
    }
    result = await pipeline.validate(record)
    assert result["severity"] == "high"


@pytest.mark.asyncio
async def test_pipeline_validate_rejects_bad_severity() -> None:
    """Invalid severity values are rejected."""
    pipeline = ThreatFeedPipeline(name="threat_feed")
    record = {
        "external_id": "TF-BAD",
        "name": "Bad Threat",
        "description": "Invalid severity",
        "severity": "apocalyptic",
        "likelihood": 0.5,
    }
    with pytest.raises(Exception):
        await pipeline.validate(record)


@pytest.mark.asyncio
async def test_pipeline_validate_rejects_bad_likelihood() -> None:
    """Likelihood outside 0-1 range is rejected."""
    pipeline = ThreatFeedPipeline(name="threat_feed")
    record = {
        "external_id": "TF-BAD",
        "name": "Bad Threat",
        "description": "Invalid likelihood",
        "severity": "low",
        "likelihood": 5.0,
    }
    with pytest.raises(Exception):
        await pipeline.validate(record)


@pytest.mark.asyncio
async def test_pipeline_full_run_succeeds() -> None:
    """Full pipeline run completes successfully."""
    pipeline = ThreatFeedPipeline(name="threat_feed")
    result = await pipeline.run()
    assert result.records_processed > 0
    assert result.records_failed == 0
    assert result.success is True


def test_threat_feed_record_normalizes_severity() -> None:
    """Severity values are lowercased."""
    record = ThreatFeedRecord(
        external_id="TF-001",
        name="Test",
        description="Test",
        severity="HIGH",
    )
    assert record.severity == "high"
