"""Synapse package bootstrap.

This repo starts as a lightweight scaffold for the CLI-first research
context layer described in Notion. Heavy integrations are intentionally
optional at this stage.
"""

from .cli import app as cli_app
from .config import Settings, get_settings
from .server import app as api_app
from .server import create_app

__all__ = [
    "__version__",
    "Settings",
    "api_app",
    "cli_app",
    "create_app",
    "get_settings",
]

__version__ = "0.1.0"

