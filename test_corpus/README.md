# Test Corpus Contract

`test_corpus/` — это не случайная папка с PDF. Это repo-side fixture layer для manifest, mirrors и metadata вокруг ingest, provenance и retrieval.

Канонический источник реальных golden PDF сейчас описан в [`docs/test-corpus.md`](../docs/test-corpus.md) и находится вне репо: `/Users/timsmykov/Desktop/Статьи для теста`.

## Minimum Coverage

В baseline corpus должны быть как минимум:

- 1 статья по медицине с таблицами клинических исходов
- 1 статья по биологии с figure panels и captions
- 1 статья по физике или math-heavy domain с формулами
- 1 статья по computer science с multi-column layout
- 1 статья со сложной таблицей и merged cells

## File Naming

Если PDF зеркалится внутрь `test_corpus/` для технических нужд, используем стабильные имена:

- `01-medicine-rct.pdf`
- `02-biology-figures.pdf`
- `03-physics-formulas.pdf`
- `04-cs-multicolumn.pdf`
- `05-complex-table.pdf`

Не переименовываем файлы после того, как они попали в golden corpus.

## Required Sidecar Metadata

Для каждого PDF должен быть metadata entry в `corpus-manifest.template.json` со следующими полями:

- `document_id`
- `file_name`
- `domain`
- `layout_features`
- `expected_artifacts`
- `notes`

## Required Layout Features

`layout_features` должен явно фиксировать, есть ли в документе:

- `tables`
- `merged_cells`
- `formulas`
- `figures`
- `charts`
- `multi_column`
- `citations`

## Expected Artifacts

`expected_artifacts` фиксирует минимальные ожидания для ingest:

- `sections`
- `tables`
- `table_cells`
- `formulas`
- `figures`
- `citations`

## Rule

Пока документ не описан в manifest, он не считается частью рабочего test corpus.
Пока документ не выбран из внешнего source folder и не синхронизирован в server-side corpus location, он не считается активным golden fixture.
