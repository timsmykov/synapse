# Synapse Implementation Checklist

Этот документ сводит Notion-источники `Synapse`, `Технический стек`, `Pre-launch Checklist` и `Roadmap — MVP за 5 дней` в один технический execution checklist.

Primary navigation:
- [`docs/master-roadmap.md`](./master-roadmap.md) for the single operational roadmap
- this file for phase-by-phase checkbox status and closeout

Принцип простой: идём строго сверху вниз. Пока незакрытые пункты текущей фазы не завершены, в следующую фазу не прыгаем.

## Phase 0. Repo And Runtime Foundation

- [x] Полностью удалить старый landing/static-site код и заменить репо на новый Synapse scaffold.
- [x] Поднять Python package baseline: `pyproject.toml`, console entrypoint, `README`, `Makefile`, `Dockerfile`.
- [x] Поднять локальный infra skeleton: `docker-compose.yml` с `Postgres + pgvector`, `Redis`, `MinIO`.
- [x] Зафиксировать runtime config в `.env.example`.
- [x] Ввести канонический `domain`-слой для provenance/artifact/task contracts.
- [x] Ввести `services`-слой как общий use-case boundary между CLI и API.
- [x] Зарезервировать пакеты `ingest/`, `storage/`, `retrieval/`, `primitives/`.
- [x] Дать smoke-level tests для config, CLI, service layer и API health/contracts.
- [x] Зафиксировать fixture layout для `test_corpus/`: какие PDF туда кладём, как именуем, какие домены покрываем.
- [x] Зафиксировать evaluation contract в `eval/`: какие метрики считаем обязательными для Day 1-2.

## Phase 1. Ingestion Contract And Parsing Pipeline

- [ ] Реализовать `Docling` adapter в `src/synapse/ingest/`.
- [ ] Реализовать `GROBID` metadata/citation adapter в `src/synapse/ingest/`.
- [ ] Зафиксировать merge-contract: как `Docling` и `GROBID` собираются в один `DocumentRecord`.
- [ ] Сделать реальный `synapse ingest <path>` для одного PDF.
- [ ] Поддержать batch ingest для директории / glob.
- [ ] Обеспечить сохранение provenance для каждого artifact: `source_document_id`, `page_number`, `bbox`, `parser`, `confidence`.
- [ ] Писать structured JSON output из ingest до подключения БД, чтобы отладить shape без infra-chaos.
- [ ] Добавить contract tests на shape `DocumentRecord`, `Section`, `TableArtifact`, `FormulaArtifact`, `FigureArtifact`.
- [ ] Добавить golden fixtures на 3-5 научных PDF с таблицами, формулами и multi-column layout.

## Phase 2. Storage And Persistence Layer

- [ ] Определить storage interfaces: document store, artifact store, task/event store.
- [ ] Реализовать PostgreSQL schema/migrations для documents, artifacts, provenance metadata, task receipts.
- [ ] Реализовать MinIO-backed binary/object storage для raw PDFs и extracted figures.
- [ ] Зафиксировать mapping `domain -> storage` без дублирования shape.
- [ ] Реализовать persistence path из `ingest` в Postgres и MinIO.
- [ ] Добавить bootstrap/init path для local infra: DB init, bucket creation, minimal health checks.
- [ ] Добавить integration tests на local Postgres/MinIO contract.

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

## Closed Now

Ниже то, что уже закрыто текущим baseline:

- [x] Новый backend/CLI scaffold вместо старого лендинга.
- [x] `domain` + provenance contracts.
- [x] `services` boundary.
- [x] Reserved package boundaries.
- [x] Smoke tests и reproducible local Python setup.

## Next Up

Следующий правильный execution slice:

1. Реализовать `Docling` adapter.
2. Реализовать `GROBID` adapter.
3. Собрать первый реальный `synapse ingest <pdf>` с `DocumentRecord` JSON output.
4. Прогнать ingest на первом golden fixture и проверить gates из `eval/contracts.md`.

Пока эти 4 пункта не закрыты, не стоит уходить глубже в retrieval или science primitives.
