"""Base class for all ETL pipelines."""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from src.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PipelineResult:
    """Outcome of a pipeline run."""

    pipeline_name: str
    records_processed: int = 0
    records_failed: int = 0
    errors: list[dict[str, str]] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None

    @property
    def success(self) -> bool:
        return self.records_failed == 0

    def record_error(self, record_id: str, message: str) -> None:
        self.errors.append({"record_id": record_id, "error": message})
        self.records_failed += 1

    def finalize(self) -> None:
        self.completed_at = datetime.now(timezone.utc)


class BasePipeline(abc.ABC):
    """Abstract base for ETL pipelines.

    Subclasses implement extract/validate/transform/load.
    The `run()` method orchestrates them in order.
    """

    def __init__(self, name: str, batch_size: int = 500) -> None:
        self.name = name
        self.batch_size = batch_size
        self.logger = get_logger(f"etl.{name}")

    async def run(self) -> PipelineResult:
        """Execute the full ETL pipeline."""
        result = PipelineResult(pipeline_name=self.name)
        self.logger.info("pipeline_started", pipeline=self.name)

        try:
            raw_data = await self.extract()
            self.logger.info("extract_complete", record_count=len(raw_data))

            validated = []
            for i, record in enumerate(raw_data):
                try:
                    validated.append(await self.validate(record))
                except Exception as e:
                    result.record_error(
                        record_id=str(record.get("id", i)), message=str(e)
                    )
                    self.logger.warning(
                        "validation_failed", record_index=i, error=str(e)
                    )

            transformed = await self.transform(validated)
            await self.load(transformed)
            result.records_processed = len(transformed)

        except Exception as e:
            self.logger.error("pipeline_failed", error=str(e))
            raise
        finally:
            result.finalize()
            self.logger.info(
                "pipeline_complete",
                processed=result.records_processed,
                failed=result.records_failed,
            )

        return result

    @abc.abstractmethod
    async def extract(self) -> list[dict[str, Any]]:
        """Pull raw data from source."""

    @abc.abstractmethod
    async def validate(self, record: dict[str, Any]) -> dict[str, Any]:
        """Validate a single raw record."""

    @abc.abstractmethod
    async def transform(self, records: list[dict[str, Any]]) -> list[Any]:
        """Transform validated records into domain objects."""

    @abc.abstractmethod
    async def load(self, records: list[Any]) -> None:
        """Upsert records to the database."""
