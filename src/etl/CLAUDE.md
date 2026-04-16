# ETL Pipeline Development

## Adding a New ETL Pipeline
1. Create a new file in `src/etl/` named `<source>_<entity>_pipeline.py`.
2. Inherit from `BasePipeline` in `src/etl/base.py`.
3. Implement: `extract()`, `validate()`, `transform()`, `load()`.
4. Register the pipeline in `src/etl/registry.py`.
5. Add a job definition in `src/jobs/` that invokes the pipeline.
6. Write both unit tests (mock the extract step) and integration tests.

## Idempotency Rules
- Every `load()` must use `ON CONFLICT ... DO UPDATE` (upsert).
- Natural keys are defined per entity in the model's `__table_args__`.
- Never use auto-increment IDs as merge keys across systems.

## Error Handling in Pipelines
- Individual record failures should NOT abort the entire batch.
- Use `PipelineResult` to track: `records_processed`, `records_failed`,
  `errors` (list of `{record_id, error_message}`).
- Log every failure at WARNING level with the record's natural key.
- The job runner writes the `PipelineResult` to `etl_job_runs`.

## Rate Limiting & Retries
- External API calls in `extract()` must use the `RateLimiter` from utils.
- Retry transient failures (HTTP 429, 503) up to 3 times with exponential backoff.
- Non-transient failures (4xx) fail immediately.
