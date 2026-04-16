"""Domain-specific exceptions for the CloudGov platform."""


class CloudGovError(Exception):
    """Base exception for all platform errors."""

    def __init__(self, message: str, code: str | None = None) -> None:
        self.message = message
        self.code = code or "INTERNAL_ERROR"
        super().__init__(self.message)


class NotFoundError(CloudGovError):
    """Raised when a requested entity does not exist."""

    def __init__(self, entity: str, identifier: str) -> None:
        super().__init__(
            message=f"{entity} not found: {identifier}",
            code="NOT_FOUND",
        )


class ValidationError(CloudGovError):
    """Raised when input data fails validation."""

    def __init__(self, message: str, field: str | None = None) -> None:
        self.field = field
        super().__init__(message=message, code="VALIDATION_ERROR")


class DuplicateError(CloudGovError):
    """Raised when attempting to create an entity that already exists."""

    def __init__(self, entity: str, identifier: str) -> None:
        super().__init__(
            message=f"{entity} already exists: {identifier}",
            code="DUPLICATE",
        )


class PipelineError(CloudGovError):
    """Raised when an ETL pipeline encounters a fatal error."""

    def __init__(self, pipeline_name: str, message: str) -> None:
        self.pipeline_name = pipeline_name
        super().__init__(
            message=f"Pipeline '{pipeline_name}' failed: {message}",
            code="PIPELINE_ERROR",
        )


class AuthorizationError(CloudGovError):
    """Raised when a user lacks permission for an operation."""

    def __init__(self, action: str, resource: str) -> None:
        super().__init__(
            message=f"Not authorized to {action} on {resource}",
            code="FORBIDDEN",
        )
