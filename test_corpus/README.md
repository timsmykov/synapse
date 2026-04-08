# Test Corpus Contract

`test_corpus/` is the repo-side fixture layer for manifest, mirrors, and metadata around ingest, provenance, and retrieval.

The canonical source of the real PDFs is outside the repo and documented in [`/Users/timsmykov/Desktop/Synapse/docs/test-corpus.md`](/Users/timsmykov/Desktop/Synapse/docs/test-corpus.md):

- `/Users/timsmykov/Desktop/Статьи для теста`

## Current Baseline

The first operational baseline now uses five real papers from that source folder and maps them to stable mirrored names:

- `01-ecommerce-meta-analysis.pdf` -> `Handoyo (2024) - Trust, Risk, Security in E-commerce Meta-analysis.pdf`
- `02-service-robot-study.pdf` -> `Belanche et al. (2021) - Robots Physical Appearance in Frontline Services.pdf`
- `03-anthropomorphism-meta-analysis.pdf` -> `Blut, M., et al. (2021) - Journal of the Academy of Marketing Science.pdf`
- `04-ai-systematic-review.pdf` -> `Hollebeek et al. (2024) - Engaging Consumers Through AI Technologies.pdf`
- `05-ai-ethics-review.pdf` -> `Masciari et al. (2024) - AI Recommendation Systems and Ethics.pdf`

This starter baseline is good enough for the first server-side ingest pass, corpus audit, and evaluation harness.
It does not yet cover the full target shape for formula-heavy, biology-panel, or clinical-RCT-specific PDFs.

## Target Coverage

Longer term, the corpus should still include:

- 1 article with strong table-heavy review or meta-analysis structure
- 1 article with figure-heavy or conceptual-model layout
- 1 formula-heavy paper
- 1 clean multi-column journal paper
- 1 document with complex or merged tables

## File Naming

When the selected PDFs are mirrored into a technical corpus directory, use these stable names:

- `01-ecommerce-meta-analysis.pdf`
- `02-service-robot-study.pdf`
- `03-anthropomorphism-meta-analysis.pdf`
- `04-ai-systematic-review.pdf`
- `05-ai-ethics-review.pdf`

Do not rename files after they are accepted into the baseline.

## Required Sidecar Metadata

Each entry in `corpus-manifest.template.json` should contain:

- `document_id`
- `file_name`
- `domain`
- `source_path`
- `source_title`
- `page_count`
- `layout_features`
- `expected_artifacts`
- `notes`

## Required Layout Features

`layout_features` should capture whether the document contains:

- `tables`
- `merged_cells`
- `formulas`
- `figures`
- `charts`
- `multi_column`
- `citations`

## Expected Artifacts

`expected_artifacts` stores minimum expectations for ingest, not exact final counts:

- `sections`
- `tables`
- `table_cells`
- `formulas`
- `figures`
- `citations`

## Sync Rule

A document is not an active golden fixture until:

1. it is described in the manifest;
2. it exists in the external source folder; and
3. it has been mirrored into a server-side or local execution corpus directory under the canonical filename.

Use [`/Users/timsmykov/Desktop/Synapse/scripts/sync_test_corpus.py`](/Users/timsmykov/Desktop/Synapse/scripts/sync_test_corpus.py) to perform that mirror step.
