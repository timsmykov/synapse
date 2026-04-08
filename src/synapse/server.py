"""FastAPI application scaffold for Synapse.

The real API surface will grow after the core research pipeline is wired in.
This module keeps a minimal health/info surface available now.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .config import Settings, get_settings
from .runtime_health import build_runtime_health_report

try:  # pragma: no cover - exercised when FastAPI is installed later.
    from fastapi import FastAPI as _FastAPI
except ModuleNotFoundError:  # pragma: no cover - current clean environment.
    _FastAPI = None


@dataclass(slots=True)
class Route:
    path: str
    endpoint: Callable[..., Any]
    methods: tuple[str, ...]


class _FallbackFastAPI:
    """Small FastAPI-compatible shim for dependency-light bootstrapping."""

    def __init__(self, *, title: str, version: str) -> None:
        self.title = title
        self.version = version
        self.routes: list[Route] = []

    def get(self, path: str):
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.routes.append(Route(path=path, endpoint=func, methods=("GET",)))
            return func

        return decorator


def create_app(settings: Settings | None = None) -> Any:
    runtime = settings or get_settings()
    report = build_runtime_health_report(runtime)
    if _FastAPI is None:
        app = _FallbackFastAPI(title=runtime.app_name, version=runtime.version)
    else:  # pragma: no cover - only when FastAPI is installed.
        app = _FastAPI(title=runtime.app_name, version=runtime.version)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "environment": report.environment,
            "deployment_target": report.deployment_target,
        }

    @app.get("/ready")
    def ready() -> dict[str, Any]:
        return report.model_dump(mode="json")

    @app.get("/info")
    def info() -> dict[str, Any]:
        return {
            "app_name": runtime.app_name,
            "environment": runtime.environment,
            "version": runtime.version,
            "deployment_target": report.deployment_target,
            "public_base_url": report.public_base_url,
            "reverse_proxy": report.reverse_proxy,
            "service_endpoints": report.service_endpoints,
            "warnings": report.warnings,
            "components": [
                "cli-first",
                "docling",
                "grobid",
                "mineru",
                "postgres",
                "minio",
                "redis",
                "llamaindex",
            ],
        }

    return app


app = create_app()
