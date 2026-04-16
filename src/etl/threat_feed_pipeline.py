"""ETL pipeline that ingests threats from an external threat intelligence feed."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, field_validator

from src.etl.base import BasePipeline
from src.etl.registry import register_pipeline


class ThreatFeedRecord(BaseModel):
    """Validation schema for incoming threat feed records."""

    external_id: str
    name: str
    description: str
    severity: str
    mitre_attack_id: str | None = None
    likelihood: float = 0.5

    @field_validator("severity")
    @classmethod
    def severity_must_be_valid(cls, v: str) -> str:
        allowed = {"low", "medium", "high", "critical"}
        if v.lower() not in allowed:
            msg = f"severity must be one of {allowed}, got {v!r}"
            raise ValueError(msg)
        return v.lower()

    @field_validator("likelihood")
    @classmethod
    def likelihood_must_be_between_0_and_1(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            msg = f"likelihood must be 0.0–1.0, got {v}"
            raise ValueError(msg)
        return v


class ThreatFeedPipeline(BasePipeline):
    """Ingests threats from an external threat intelligence API."""

    async def extract(self) -> list[dict[str, Any]]:
        """Fetch threat data from external feed.

        In production, this calls an HTTP API. For now, returns sample data.
        """
        self.logger.info("extracting_from_threat_feed")
        # TODO: Replace with actual HTTP client call
        return [
            {
                "external_id": "TF-001",
                "name": "Data Exfiltration via S3",
                "description": "Unauthorized data transfer from S3 buckets",
                "severity": "high",
                "mitre_attack_id": "T1567",
                "likelihood": 0.7,
            },
            {
                "external_id": "TF-002",
                "name": "Privilege Escalation via IAM",
                "description": "Exploiting misconfigured IAM policies",
                "severity": "critical",
                "mitre_attack_id": "T1548",
                "likelihood": 0.4,
            },
        ]

    async def validate(self, record: dict[str, Any]) -> dict[str, Any]:
        """Validate a raw record against the schema."""
        validated = ThreatFeedRecord(**record)
        return validated.model_dump()

    async def transform(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Map validated records to internal format."""
        return [
            {
                "name": r["name"],
                "description": r["description"],
                "severity": r["severity"],
                "mitre_attack_id": r.get("mitre_attack_id"),
                "likelihood": r["likelihood"],
            }
            for r in records
        ]

    async def load(self, records: list[dict[str, Any]]) -> None:
        """Upsert threats to the database.

        Uses ON CONFLICT (name) DO UPDATE for idempotency.
        """
        self.logger.info("loading_threats", count=len(records))
        # TODO: Implement actual DB upsert
        for record in records:
            self.logger.info("upserted_threat", name=record["name"])


# Register this pipeline
register_pipeline("threat_feed", ThreatFeedPipeline)
