"""FastAPI application scaffold for Synapse.

The real API surface will grow after the core research pipeline is wired in.
This module keeps a minimal health/info surface available now.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .services import doctor_workflow

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


def create_app() -> Any:
    report = doctor_workflow()
    if _FastAPI is None:
        app = _FallbackFastAPI(title=report.app_name, version=report.version)
    else:  # pragma: no cover - only when FastAPI is installed.
        app = _FastAPI(title=report.app_name, version=report.version)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/info")
    def info() -> dict[str, Any]:
        return {
            "app_name": report.app_name,
            "environment": report.environment,
            "version": report.version,
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
