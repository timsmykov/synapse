# Evaluation Contract

`eval/` фиксирует обязательные метрики и acceptance gates для первых технических фаз.

## Day 1 Gates

Для ingest baseline обязательны:

- `table_extraction_accuracy`
- `formula_fidelity`
- `provenance_correctness`
- `section_order_correctness`

## Day 2 Gates

После подключения storage/retrieval добавляются:

- `artifact_persistence_integrity`
- `retrieval_result_provenance_integrity`
- `document_filter_correctness`

## Metric Definitions

### `table_extraction_accuracy`

Сравнение expected table structure/cells из golden corpus против extracted output.

Минимальный MVP target:

- `>= 0.95` на baseline corpus

### `formula_fidelity`

Доля формул, где extracted LaTeX сохраняет математический смысл и структуру.

Минимальный MVP target:

- `>= 0.95` на formula fixtures

### `provenance_correctness`

Доля artifacts, где корректны:

- `source_document_id`
- `page_number`
- `bbox` при наличии
- `parser`
- `confidence`

Минимальный MVP target:

- `1.00` для обязательных provenance fields

### `section_order_correctness`

Проверка, что logical reading order и headings не деградировали после parsing.

Минимальный MVP target:

- `>= 0.95`

### `artifact_persistence_integrity`

Проверка, что artifact shape до и после persistence идентичен по обязательным полям.

Минимальный MVP target:

- `1.00`

### `retrieval_result_provenance_integrity`

Проверка, что query results не теряют provenance metadata.

Минимальный MVP target:

- `1.00`

### `document_filter_correctness`

Проверка, что retrieval filters по `document_id`, `artifact_type`, `page_number` работают без leakage.

Минимальный MVP target:

- `1.00`

## Rule

Новая parser/storage/retrieval интеграция не считается принятой, пока не проходит соответствующие gates на baseline corpus.

