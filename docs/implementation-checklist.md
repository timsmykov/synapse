# Synapse Implementation Checklist

Этот документ сводит Notion-источники `Synapse`, `Технический стек`, `Pre-launch Checklist` и `Roadmap — MVP за 5 дней` в один технический execution checklist.

Primary navigation:
- [`docs/master-roadmap.md`](./master-roadmap.md) for the single operational roadmap
- this file for phase-by-phase checkbox status and closeout

Принцип простой: идём строго сверху вниз. Пока незакрытые пункты текущей фазы не завершены, в следующую фазу не прыгаем.

## Phase 0. Repo And Runtime Foundation

- [x] Полностью удалить старый landing/static-site код и заменить репо на новый Synapse scaffold.
- [x] Поднять Python package baseline: `pyproject.toml`, console entrypoint, `README`, `Makefile`, `Dockerfile`.
- [x] Поднять compose infra skeleton: `docker-compose.yml` с `Postgres + pgvector`, `Redis`, `MinIO`.
- [x] Зафиксировать runtime config в `.env.example`.
- [x] Ввести канонический `domain`-слой для provenance/artifact/task contracts.
- [x] Ввести `services`-слой как общий use-case boundary между CLI и API.
- [x] Зарезервировать пакеты `ingest/`, `storage/`, `retrieval/`, `primitives/`.
- [x] Дать smoke-level tests для config, CLI, service layer и API health/contracts.
- [x] Зафиксировать fixture layout для `test_corpus/`: какие PDF туда кладём, как именуем, какие домены покрываем.
- [x] Зафиксировать evaluation contract в `eval/`: какие метрики считаем обязательными для Day 1-2.

## Phase 1. Ingestion Contract And Parsing Pipeline

Phase 1 status: partially verified. The canonical VPS `app`-container canary is green, and the currently installed five-document server corpus passes as a full batch when evaluated against the matching server-side manifest. The remaining blocker is corpus-contract drift between the repo-local manifest and the server golden-corpus manifest. See `docs/phase-1-verification.md`.

Execution rule for this phase:

- one owner for `scaffold`
- separate owners for `docling`, `grobid`, and `merge/eval`
- no parallel edits to shared integration seams such as `services/`, `cli`, `config`, deploy scripts, or roadmap/checklist docs

- [x] Реализовать `Docling` adapter в `src/synapse/ingest/`.
- [x] Реализовать `GROBID` metadata/citation adapter в `src/synapse/ingest/`.
- [x] Зафиксировать merge-contract: как `Docling` и `GROBID` собираются в один `DocumentRecord`.
- [x] Сделать реальный `synapse ingest <path>` для одного PDF.
- [x] Поддержать batch ingest для директории / glob.
- [x] Обеспечить provenance envelope для каждого artifact: `source_document_id`, `page_number`, `parser`, а также parser-provided `bbox` / `confidence` там, где парсер реально их отдаёт.
- [x] Писать structured JSON output из ingest до подключения БД, чтобы отладить shape без infra-chaos.
- [x] Добавить contract tests на shape `DocumentRecord`, `Section`, `TableArtifact`, `FormulaArtifact`, `FigureArtifact`.
- [x] Добавить golden fixtures на 3-5 научных PDF с таблицами, формулами и multi-column layout.
- [ ] Свести repo-local fixture manifest и server golden-corpus manifest к одному canonical fixture set и зафиксировать `docs/phase-1-verification.md`.

## Phase 2. Storage And Persistence Layer

- [ ] Определить storage interfaces: document store, artifact store, task/event store.
- [ ] Реализовать PostgreSQL schema/migrations для documents, artifacts, provenance metadata, task receipts.
- [ ] Реализовать MinIO-backed binary/object storage для raw PDFs и extracted figures.
- [ ] Зафиксировать mapping `domain -> storage` без дублирования shape.
- [ ] Реализовать persistence path из `ingest` в Postgres и MinIO.
- [ ] Добавить bootstrap/init path для server compose infra: DB init, bucket creation, minimal health checks.
- [ ] Добавить integration tests на server Postgres/MinIO contract.

## Phase 3. Retrieval And Indexing Layer

- [ ] Зафиксировать retrieval contract: query result shape, scoring, provenance payload.
- [ ] Реализовать базовый repository/query layer поверх Postgres.
- [ ] Подключить `LlamaIndex` как indexing facade, не смешивая его с domain models.
- [ ] Реализовать хотя бы один end-to-end retrieval path: document -> section -> table.
- [ ] Поддержать `synapse query "<prompt>"` с structured output.
- [ ] Добавить metadata filters: `document_id`, `page_number`, `artifact_type`, `citation year`.
- [ ] Добавить contract tests на retrieval result shape и provenance preservation.

## Phase 4. Advanced Parsing For Figures And Formulas

- [ ] Ввести adapter boundary под `MinerU` или `PDF-Extract-Kit`.
- [ ] Добавить extraction path для figures, charts и formulas, не ломая базовый Docling pipeline.
- [ ] Зафиксировать merge-rules между base parser artifacts и advanced parser artifacts.
- [ ] Добавить quality gates: table fidelity, formula fidelity, figure caption/data extraction completeness.
- [ ] Обновить `DocumentRecord` population так, чтобы advanced artifacts были first-class citizens в retrieval.

## Phase 5. Science Primitives And Orchestration

- [ ] Реализовать первый primitive: `ConsistencyDetector`.
- [ ] Реализовать второй primitive: `TableValidator`.
- [ ] Реализовать третий primitive: `PICOExtractor`.
- [ ] Добавить orchestration path для `analyze` через `services` слой.
- [ ] Подключить минимальный async contract для долгих задач: queued/running/succeeded/failed.
- [ ] Добавить structured analysis output с ссылками на source provenance.
- [ ] Добавить tests на primitive contracts и end-to-end `analyze` payload shape.

## Phase 6. Hardening And Release Baseline

- [ ] Привести `synapse ingest`, `synapse query`, `synapse analyze`, `synapse doctor` к стабильным CLI contracts.
- [ ] Добавить Python SDK поверх service layer, а не поверх CLI.
- [ ] Закрыть README/examples реальными командами и expected output.
- [ ] Добавить smoke flow: `docker compose up` -> ingest -> query -> analyze.
- [ ] Зафиксировать acceptance criteria для MVP на одном понятном dataset.
- [x] Поднять CI pipeline для `ruff`, `pytest`, contract tests и compose smoke checks.
- [x] Зафиксировать remote testing baseline на single-node VPS: `app`, `postgres`, `redis`, `minio`, `grobid`, reverse proxy.
- [ ] Закрыть deploy hardening для testing/staging: non-root deploy user, HTTPS, закрытые internal ports, backup policy для Postgres и MinIO.
- [ ] Зафиксировать триггеры, когда staging и production должны быть разведены на разные узлы.

## Closed Now

Ниже то, что уже закрыто текущим baseline:

- [x] Новый backend/CLI scaffold вместо старого лендинга.
- [x] `domain` + provenance contracts.
- [x] `services` boundary.
- [x] Reserved package boundaries.
- [x] Smoke tests и reproducible Python setup.
- [x] Явная Phase 0 verification sweep зафиксирована в `docs/phase-0-verification.md`.

## Next Up

Следующий правильный execution slice:

1. Свести `test_corpus/corpus-manifest.json` и `/srv/synapse/test_corpus/golden/corpus-manifest.json` к одному canonical fixture set.
2. Повторно прогнать canonical full-batch evaluation на этом unified contract и обновить `docs/phase-1-verification.md`.
3. После этого перейти к storage interfaces и persistence path в Postgres/MinIO.

Пока эти 4 пункта не закрыты, не стоит уходить глубже в retrieval или science primitives.

## Ownership model

Scaffold owner:

- `src/synapse/config.py`
- `src/synapse/cli.py`
- `src/synapse/server.py`
- `src/synapse/domain/`
- `src/synapse/services/`
- `deploy/`
- `scripts/deploy_staging.sh`
- `scripts/check_staging.sh`
- `scripts/run_ingest_smoke.sh`
- roadmap/checklist/verification docs

Component owners:

- `Docling`: `src/synapse/ingest/docling_adapter.py` and Docling-specific tests
- `GROBID`: `src/synapse/ingest/grobid_adapter.py` and GROBID-specific tests
- `Merge/normalize`: `src/synapse/ingest/merge.py`, `src/synapse/ingest/models.py`, merge/domain contract tests
- `Evaluation/golden`: evaluation logic, corpus manifest, metric thresholds, verification analysis

Rule:

- component owners do not edit scaffold files unless that write scope is explicitly reassigned for a narrow integration task

## Environment Policy

- Локальная машина используется для редактирования кода и хранения исходных PDF, но не как обязательная runtime/install среда.
- Общий VPS является основной средой установки, тестов, runtime и testing/integration.
- До отдельного production node допускается один VPS для testing и приватных demo-нагрузок, но без тяжёлого локального LLM inference на той же машине.
- Текущий testing target: `ssh root@194.163.181.122`.
- Локальный Mac не используется для project-local `.venv`, local compose stack, deploy smoke или acceptance tests по Synapse.
- Если такие локальные runtime-артефакты появляются, их нужно удалять и продолжать работу только через сервер.
