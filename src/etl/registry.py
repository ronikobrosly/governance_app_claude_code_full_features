"""Registry for ETL pipelines — add new pipelines here."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.etl.base import BasePipeline

# Maps pipeline name -> factory function
_REGISTRY: dict[str, type["BasePipeline"]] = {}


def register_pipeline(name: str, pipeline_cls: type["BasePipeline"]) -> None:
    """Register a pipeline class by name."""
    _REGISTRY[name] = pipeline_cls


def get_pipeline(name: str, **kwargs: object) -> "BasePipeline":
    """Instantiate a registered pipeline by name."""
    if name not in _REGISTRY:
        raise KeyError(f"Unknown pipeline: {name!r}. Registered: {list(_REGISTRY)}")
    return _REGISTRY[name](name=name, **kwargs)


def list_pipelines() -> list[str]:
    """Return all registered pipeline names."""
    return sorted(_REGISTRY.keys())
