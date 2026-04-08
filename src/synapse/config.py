"""Configuration helpers for Synapse.

The initial scaffold keeps configuration small and dependency-free so the
package is importable before the full stack is wired in.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

DEFAULT_APP_NAME = "Synapse"
DEFAULT_ENVIRONMENT = "development"
DEFAULT_VERSION = "0.1.0"
DEFAULT_DATA_DIR = Path("data")
DEFAULT_CORPUS_DIR = Path("test_corpus")
DEFAULT_EVAL_DIR = Path("eval")
DEFAULT_DATABASE_URL = "postgresql+psycopg://synapse:synapse@localhost:5432/synapse"
DEFAULT_REDIS_URL = "redis://localhost:6379/0"
DEFAULT_MINIO_ENDPOINT = "localhost:9000"
DEFAULT_MINIO_ACCESS_KEY = "minioadmin"
DEFAULT_MINIO_SECRET_KEY = "minioadmin"
DEFAULT_MINIO_BUCKET = "synapse-artifacts"
DEFAULT_LLM_PROVIDER = "ollama"
DEFAULT_PARSER = "docling"
DEFAULT_EMBEDDING_MODEL = "specter2"
DEFAULT_DEPLOYMENT_TARGET = "local"
DEFAULT_PUBLIC_BASE_URL = ""
DEFAULT_REVERSE_PROXY = "none"
DEFAULT_GROBID_URL = "http://localhost:8070"
DEFAULT_INGEST_CONCURRENCY = 1


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings derived from environment variables."""

    app_name: str = DEFAULT_APP_NAME
    environment: str = DEFAULT_ENVIRONMENT
    version: str = DEFAULT_VERSION
    data_dir: Path = DEFAULT_DATA_DIR
    corpus_dir: Path = DEFAULT_CORPUS_DIR
    eval_dir: Path = DEFAULT_EVAL_DIR
    database_url: str = DEFAULT_DATABASE_URL
    redis_url: str = DEFAULT_REDIS_URL
    minio_endpoint: str = DEFAULT_MINIO_ENDPOINT
    minio_access_key: str = DEFAULT_MINIO_ACCESS_KEY
    minio_secret_key: str = DEFAULT_MINIO_SECRET_KEY
    minio_bucket: str = DEFAULT_MINIO_BUCKET
    llm_provider: str = DEFAULT_LLM_PROVIDER
    default_parser: str = DEFAULT_PARSER
    default_embedding_model: str = DEFAULT_EMBEDDING_MODEL
    deployment_target: str = DEFAULT_DEPLOYMENT_TARGET
    public_base_url: str = DEFAULT_PUBLIC_BASE_URL
    reverse_proxy: str = DEFAULT_REVERSE_PROXY
    grobid_url: str = DEFAULT_GROBID_URL
    ingest_concurrency: int = DEFAULT_INGEST_CONCURRENCY

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            app_name=os.getenv("SYNAPSE_APP_NAME", DEFAULT_APP_NAME),
            environment=os.getenv("SYNAPSE_ENV", DEFAULT_ENVIRONMENT),
            version=os.getenv("SYNAPSE_VERSION", DEFAULT_VERSION),
            data_dir=Path(os.getenv("SYNAPSE_DATA_DIR", str(DEFAULT_DATA_DIR))),
            corpus_dir=Path(os.getenv("SYNAPSE_CORPUS_DIR", str(DEFAULT_CORPUS_DIR))),
            eval_dir=Path(os.getenv("SYNAPSE_EVAL_DIR", str(DEFAULT_EVAL_DIR))),
            database_url=os.getenv("SYNAPSE_DATABASE_URL", DEFAULT_DATABASE_URL),
            redis_url=os.getenv("SYNAPSE_REDIS_URL", DEFAULT_REDIS_URL),
            minio_endpoint=os.getenv("SYNAPSE_MINIO_ENDPOINT", DEFAULT_MINIO_ENDPOINT),
            minio_access_key=os.getenv("SYNAPSE_MINIO_ACCESS_KEY", DEFAULT_MINIO_ACCESS_KEY),
            minio_secret_key=os.getenv("SYNAPSE_MINIO_SECRET_KEY", DEFAULT_MINIO_SECRET_KEY),
            minio_bucket=os.getenv("SYNAPSE_MINIO_BUCKET", DEFAULT_MINIO_BUCKET),
            llm_provider=os.getenv("SYNAPSE_LLM_PROVIDER", DEFAULT_LLM_PROVIDER),
            default_parser=os.getenv("SYNAPSE_DEFAULT_PARSER", DEFAULT_PARSER),
            default_embedding_model=os.getenv(
                "SYNAPSE_DEFAULT_EMBEDDING_MODEL",
                DEFAULT_EMBEDDING_MODEL,
            ),
            deployment_target=os.getenv(
                "SYNAPSE_DEPLOYMENT_TARGET",
                DEFAULT_DEPLOYMENT_TARGET,
            ),
            public_base_url=os.getenv(
                "SYNAPSE_PUBLIC_BASE_URL",
                DEFAULT_PUBLIC_BASE_URL,
            ),
            reverse_proxy=os.getenv(
                "SYNAPSE_REVERSE_PROXY",
                DEFAULT_REVERSE_PROXY,
            ),
            grobid_url=os.getenv("SYNAPSE_GROBID_URL", DEFAULT_GROBID_URL),
            ingest_concurrency=max(
                1,
                int(
                    os.getenv(
                        "SYNAPSE_INGEST_CONCURRENCY",
                        str(DEFAULT_INGEST_CONCURRENCY),
                    )
                ),
            ),
        )

    @property
    def summary(self) -> dict[str, str]:
        """Machine-friendly summary used by the API and CLI."""

        return {
            "app_name": self.app_name,
            "environment": self.environment,
            "version": self.version,
            "data_dir": str(self.data_dir),
            "corpus_dir": str(self.corpus_dir),
            "eval_dir": str(self.eval_dir),
            "database_url": self.database_url,
            "redis_url": self.redis_url,
            "minio_endpoint": self.minio_endpoint,
            "minio_bucket": self.minio_bucket,
            "llm_provider": self.llm_provider,
            "default_parser": self.default_parser,
            "default_embedding_model": self.default_embedding_model,
            "deployment_target": self.deployment_target,
            "public_base_url": self.public_base_url,
            "reverse_proxy": self.reverse_proxy,
            "grobid_url": self.grobid_url,
            "ingest_concurrency": str(self.ingest_concurrency),
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings for the current process."""

    return Settings.from_env()
