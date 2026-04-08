# Synapse Deployment Baseline

This document is the deployment and operations baseline for the first remote Synapse environment.

## Target

- Current staging host: `ssh root@194.163.181.122`
- `root` access is acceptable for first-time machine provisioning only.
- Day-to-day deploys should move to a dedicated non-root deploy user.

## Topology

The first remote environment is a single self-hosted VPS running Docker Compose.

Planned services:

- `reverse-proxy` for HTTPS termination and public ingress
- `app` for the FastAPI control plane
- `worker` for background ingest/analyze execution
- `postgres` for primary data and pgvector
- `redis` for queue/transient workflow state
- `minio` for raw PDFs and extracted artifacts
- `grobid` for metadata extraction

## Network Policy

Public:

- `80/443` on the reverse proxy

Private only:

- `postgres`
- `redis`
- `minio`
- `grobid`
- internal app and worker ports

Do not expose Postgres, Redis, MinIO, or GROBID directly to the public internet.

## Operating Rules

- Keep local development on the Mac; do not turn the VPS into the default dev box.
- Use the VPS for integrated parser/storage testing, staging smoke flows, and private demos.
- Keep ingest concurrency conservative until parser memory usage is measured on real PDFs.
- Do not colocate heavy local LLM inference on this box during the MVP phase.

## First Provisioning Checklist

1. Create a non-root deploy user with Docker permissions.
2. Install Docker Engine and Docker Compose plugin.
3. Configure the reverse proxy and DNS.
4. Prepare persistent volumes for Postgres and MinIO.
5. Copy `.env` with staging values.
6. Start the compose stack.
7. Verify health endpoints and service reachability.

## Deploy Baseline

1. Pull the target git revision on the server.
2. Run `docker compose pull` or rebuild images.
3. Apply database migrations when they exist.
4. Restart `app` and `worker`.
5. Run post-deploy health checks.
6. Run one ingest smoke test on a known PDF fixture.

## Readiness Expectations

A remote deployment is considered ready only when:

- reverse proxy serves the public HTTPS URL
- `app` health endpoint is reachable
- Postgres is reachable from the app
- Redis is reachable from app and worker
- MinIO bucket access works
- GROBID is reachable from the app or worker

## Rollback Baseline

If a deploy is bad:

1. revert to the previous git revision or previous image tag
2. restart the compose stack with the previous revision
3. rerun health checks
4. confirm the ingest smoke path still works

## Backup Baseline

- Postgres needs regular logical or volume-level backups.
- MinIO object data needs scheduled backup or replication.
- Backup policy should be formalized before the first production-like dataset lands on the server.
