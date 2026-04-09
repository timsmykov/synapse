"""Runtime health helpers for local, CI, and VPS deployments."""

from __future__ import annotations

from typing import Literal
from urllib.parse import urlparse

from synapse.config import Settings
from synapse.domain.common import SynapseModel

REMOTE_TARGETS = {"testing", "staging", "production"}


class RuntimeHealthCheck(SynapseModel):
    """Single runtime readiness check."""

    name: str
    status: Literal["ok", "warn", "fail"]
    detail: str


class RuntimeHealthReport(SynapseModel):
    """Deploy-aware runtime status exposed by the server health surface."""

    status: Literal["ok", "warn", "fail"] = "ok"
    app_name: str
    environment: str
    deployment_target: str
    version: str
    public_base_url: str | None = None
    reverse_proxy: str
    ingest_concurrency: int
    service_endpoints: dict[str, str]
    warnings: list[str]
    checks: list[RuntimeHealthCheck]


def build_runtime_health_report(settings: Settings) -> RuntimeHealthReport:
    deployment_target = settings.deployment_target.lower().strip() or "local"
    public_base_url = settings.public_base_url.strip() or None
    reverse_proxy = settings.reverse_proxy.strip() or "none"
    checks: list[RuntimeHealthCheck] = []

    if deployment_target in REMOTE_TARGETS:
        if not public_base_url:
            checks.append(
                RuntimeHealthCheck(
                    name="public_base_url",
                    status="warn",
                    detail=(
                        "SYNAPSE_PUBLIC_BASE_URL is empty; server deployments should "
                        "advertise the external HTTPS URL."
                    ),
                )
            )
        elif not public_base_url.startswith("https://"):
            checks.append(
                RuntimeHealthCheck(
                    name="public_base_url",
                    status="warn",
                    detail=(
                        "SYNAPSE_PUBLIC_BASE_URL should use HTTPS on "
                        "staging/production deployments."
                    ),
                )
            )
        else:
            checks.append(
                RuntimeHealthCheck(
                    name="public_base_url",
                    status="ok",
                    detail=f"external URL configured: {public_base_url}",
                )
            )

        if reverse_proxy.lower() == "none":
            checks.append(
                RuntimeHealthCheck(
                    name="reverse_proxy",
                    status="warn",
                    detail=(
                        "SYNAPSE_REVERSE_PROXY is 'none'; server deployments should sit "
                        "behind Caddy or Nginx."
                    ),
                )
            )
        else:
            checks.append(
                RuntimeHealthCheck(
                    name="reverse_proxy",
                    status="ok",
                    detail=f"reverse proxy configured: {reverse_proxy}",
                )
            )

        endpoint_checks = {
            "database_url": settings.database_url,
            "redis_url": settings.redis_url,
            "minio_endpoint": settings.minio_endpoint,
            "grobid_url": settings.grobid_url,
        }
        for name, value in endpoint_checks.items():
            if _points_to_loopback(value):
                checks.append(
                    RuntimeHealthCheck(
                        name=name,
                        status="fail",
                        detail=(
                            f"{name} points at localhost; use an internal service name "
                            "or private host on the server."
                        ),
                    )
                )
            else:
                checks.append(
                    RuntimeHealthCheck(
                        name=name,
                        status="ok",
                        detail=f"{name} points to a non-loopback address",
                    )
                )

        if settings.ingest_concurrency > 2:
            checks.append(
                RuntimeHealthCheck(
                    name="ingest_concurrency",
                    status="warn",
                    detail=(
                        "single-node VPS deployments should keep parser concurrency conservative "
                        "until memory usage is measured on real PDFs"
                    ),
                )
            )
        else:
            checks.append(
                RuntimeHealthCheck(
                    name="ingest_concurrency",
                    status="ok",
                    detail=f"ingest concurrency is set to {settings.ingest_concurrency}",
                )
            )

        if settings.llm_provider.lower() == "ollama":
            checks.append(
                RuntimeHealthCheck(
                    name="llm_provider",
                    status="warn",
                    detail=(
                        "docs discourage colocating heavy local LLM inference with "
                        "parser and storage services on the same VPS"
                    ),
                )
            )
        else:
            checks.append(
                RuntimeHealthCheck(
                    name="llm_provider",
                    status="ok",
                    detail=f"llm provider is {settings.llm_provider}",
                )
            )

        if settings.embedding_provider.lower() != "openrouter":
            checks.append(
                RuntimeHealthCheck(
                    name="embedding_provider",
                    status="warn",
                    detail=(
                        "current MVP policy expects embeddings to be routed through "
                        "OpenRouter unless a later phase explicitly changes that baseline"
                    ),
                )
            )
        else:
            checks.append(
                RuntimeHealthCheck(
                    name="embedding_provider",
                    status="ok",
                    detail="embedding provider is openrouter",
                )
            )

        if settings.parser_ocr_enabled:
            checks.append(
                RuntimeHealthCheck(
                    name="parser_ocr",
                    status="warn",
                    detail=(
                        "MVP ingest keeps OCR disabled by default; enable OCR only for "
                        "scanned or image-only PDFs after the base Docling path is stable"
                    ),
                )
            )
        else:
            checks.append(
                RuntimeHealthCheck(
                    name="parser_ocr",
                    status="ok",
                    detail="OCR is disabled for the default MVP ingest path",
                )
            )

        if settings.colpali_enabled:
            checks.append(
                RuntimeHealthCheck(
                    name="colpali",
                    status="warn",
                    detail=(
                        "ColPali is deferred from the current MVP baseline and should stay "
                        "off until the retrieval phase explicitly adopts it"
                    ),
                )
            )
        else:
            checks.append(
                RuntimeHealthCheck(
                    name="colpali",
                    status="ok",
                    detail="ColPali is deferred and currently disabled",
                )
            )
    else:
        checks.extend(
            [
                RuntimeHealthCheck(
                    name="public_base_url",
                    status="ok",
                    detail="not required for local or CI runs",
                ),
                RuntimeHealthCheck(
                    name="reverse_proxy",
                    status="ok",
                    detail="not required for local or CI runs",
                ),
                RuntimeHealthCheck(
                    name="ingest_concurrency",
                    status="ok",
                    detail=f"ingest concurrency is set to {settings.ingest_concurrency}",
                ),
                RuntimeHealthCheck(
                    name="llm_provider",
                    status="ok",
                    detail=f"llm provider is {settings.llm_provider}",
                ),
                RuntimeHealthCheck(
                    name="embedding_provider",
                    status="ok",
                    detail=f"embedding provider is {settings.embedding_provider}",
                ),
                RuntimeHealthCheck(
                    name="parser_ocr",
                    status="ok",
                    detail=(
                        "OCR flag is off" if not settings.parser_ocr_enabled else "OCR flag is on"
                    ),
                ),
                RuntimeHealthCheck(
                    name="colpali",
                    status="ok",
                    detail=(
                        "ColPali is disabled"
                        if not settings.colpali_enabled
                        else "ColPali is enabled"
                    ),
                ),
            ]
        )
        for name in ("database_url", "redis_url", "minio_endpoint", "grobid_url"):
            checks.append(
                RuntimeHealthCheck(
                    name=name,
                    status="ok",
                    detail="loopback endpoints are acceptable outside remote server targets",
                )
            )

    warnings = [check.detail for check in checks if check.status in {"warn", "fail"}]
    statuses = {check.status for check in checks}
    overall_status: Literal["ok", "warn", "fail"] = "ok"
    if "fail" in statuses:
        overall_status = "fail"
    elif "warn" in statuses:
        overall_status = "warn"

    return RuntimeHealthReport(
        status=overall_status,
        app_name=settings.app_name,
        environment=settings.environment,
        deployment_target=deployment_target,
        version=settings.version,
        public_base_url=public_base_url,
        reverse_proxy=reverse_proxy,
        ingest_concurrency=settings.ingest_concurrency,
        service_endpoints={
            "database_url": settings.database_url,
            "redis_url": settings.redis_url,
            "minio_endpoint": settings.minio_endpoint,
            "grobid_url": settings.grobid_url,
        },
        warnings=warnings,
        checks=checks,
    )


def _points_to_loopback(value: str) -> bool:
    host = _extract_host(value)
    return host in {"localhost", "127.0.0.1", "::1"}


def _extract_host(value: str) -> str:
    parsed = urlparse(value if "://" in value else f"http://{value}")
    return (parsed.hostname or "").strip().lower()
