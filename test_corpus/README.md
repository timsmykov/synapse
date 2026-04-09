# Test Corpus Contract

`test_corpus/` is the repo-side fixture layer for manifest, mirrors, and metadata around ingest, provenance, and retrieval.

The canonical source of the real PDFs is outside the repo and documented in [`/Users/timsmykov/Desktop/Synapse/docs/test-corpus.md`](/Users/timsmykov/Desktop/Synapse/docs/test-corpus.md):

- `/Users/timsmykov/Desktop/Статьи для теста`

## Current Baseline

The first operational baseline now uses five real papers from that source folder and maps them to stable mirrored names:

- `01-ecommerce-meta-analysis.pdf` -> `Handoyo (2024) - Trust, Risk, Security in E-commerce Meta-analysis.pdf`
- `02-jams-service-review.pdf` -> `Blut, M., et al. (2021) - Journal of the Academy of Marketing Science.pdf`
- `03-ebusiness-latent-topics.pdf` -> `Oprea & Bra (2025) - AI Game-Changer in E-Business.pdf`
- `04-chatbot-customer-experience.pdf` -> `Nguyen et al. (2023) - Chatbots Anthropomorphism Customer Experience.pdf`
- `05-ai-ethics-recommendation-systems.pdf` -> `Masciari et al. (2024) - AI Recommendation Systems and Ethics.pdf`

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
- `02-jams-service-review.pdf`
- `03-ebusiness-latent-topics.pdf`
- `04-chatbot-customer-experience.pdf`
- `05-ai-ethics-recommendation-systems.pdf`

Do not rename files after they are accepted into the baseline.

## Required Sidecar Metadata

Each entry in `corpus-manifest.json` should contain the fields used by the active golden baseline:

- `document_id`
- `file_name`
- `domain`
- `source_file_name`
- `layout_features`
- `expected_artifacts`
- `notes`

The historical `corpus-manifest.template.json` may include extra draft-only fields such as `source_path`, `source_title`, and `page_count`, but those are not part of the active evaluation contract.

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

Use [`/Users/timsmykov/Desktop/Synapse/scripts/sync_test_corpus.sh`](/Users/timsmykov/Desktop/Synapse/scripts/sync_test_corpus.sh) to perform that mirror step.

## Manifest Policy

- `corpus-manifest.json` is the canonical active manifest for the current golden baseline.
- `corpus-manifest.template.json` is historical scaffolding only and must not be used as the default evaluation input.
- A partial output directory is not a valid evaluation target. The active output set must cover every `document_id` in the canonical manifest before Phase 1 can be considered green.
