"""Command-line interface for Synapse.

The command names match the early MVP roadmap:
`ingest`, `query`, `analyze`, and `doctor`.
"""

from __future__ import annotations

import json
from typing import Any

from .config import get_settings

try:  # pragma: no cover - exercised when Typer is installed later.
    import typer as _typer
except ModuleNotFoundError:  # pragma: no cover - current clean environment.
    _typer = None


class _FallbackCommandApp:
    """Tiny stand-in used until Typer is added to the dependency set."""

    def __init__(self, *, help: str | None = None) -> None:
        self.help = help
        self.commands: dict[str, Any] = {}

    def command(self, name: str | None = None):
        def decorator(func):
            command_name = name or func.__name__.replace("_", "-")
            self.commands[command_name] = func
            return func

        return decorator

    def __call__(self, *args: Any, **kwargs: Any) -> int:
        raise RuntimeError("Typer is not installed in this environment.")


if _typer is None:
    app = _FallbackCommandApp(help="Synapse CLI")
else:  # pragma: no cover - only when Typer is installed.
    app = _typer.Typer(add_completion=False, help="Synapse CLI")


def _format_payload(command: str, **fields: Any) -> dict[str, Any]:
    payload = {"command": command}
    payload.update(fields)
    return payload


def _finalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if _typer is not None:
        _typer.echo(json.dumps(payload, indent=2, sort_keys=True))
    return payload


@app.command("ingest")
def ingest(
    source: str = "test_corpus",
    output: str = "data/corpus.db",
) -> dict[str, Any]:
    """Prepare a corpus ingest job."""

    return _finalize_payload(_format_payload("ingest", source=source, output=output))


@app.command("query")
def query(
    prompt: str,
    limit: int = 5,
) -> dict[str, Any]:
    """Prepare a retrieval query job."""

    return _finalize_payload(_format_payload("query", prompt=prompt, limit=limit))


@app.command("analyze")
def analyze(
    corpus: str = "data/corpus.db",
    mode: str = "systematic-review",
) -> dict[str, Any]:
    """Prepare an analysis job."""

    return _finalize_payload(_format_payload("analyze", corpus=corpus, mode=mode))


@app.command("doctor")
def doctor() -> dict[str, Any]:
    """Report the current runtime and configuration state."""

    settings = get_settings()
    return _finalize_payload(_format_payload("doctor", settings=settings.summary))


def main() -> None:
    """Entry point used by future console scripts."""

    if _typer is None:
        raise RuntimeError("Install Typer to use the interactive CLI entry point.")
    app()
