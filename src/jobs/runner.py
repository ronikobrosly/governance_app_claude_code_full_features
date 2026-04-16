"""Job runner that executes registered ETL pipelines."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from src.db import get_session
from src.etl.registry import get_pipeline
from src.models.etl_job_run import ETLJobRun, JobStatus
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def run_etl_job(pipeline_name: str) -> None:
    """Execute a pipeline and record the result in etl_job_runs."""
    logger.info("job_starting", pipeline=pipeline_name)

    pipeline = get_pipeline(pipeline_name)
    result = await pipeline.run()

    async with get_session() as session:
        job_run = ETLJobRun(
            pipeline_name=pipeline_name,
            status=JobStatus.COMPLETED if result.success else JobStatus.PARTIAL,
            records_processed=result.records_processed,
            records_failed=result.records_failed,
            error_details=str(result.errors) if result.errors else None,
            started_at=result.started_at,
            completed_at=result.completed_at or datetime.now(timezone.utc),
        )
        session.add(job_run)

    logger.info(
        "job_complete",
        pipeline=pipeline_name,
        processed=result.records_processed,
        failed=result.records_failed,
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m src.jobs.runner <pipeline_name>")
        sys.exit(1)

    asyncio.run(run_etl_job(sys.argv[1]))
