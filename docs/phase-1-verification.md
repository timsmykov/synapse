# Phase 1 Verification

Phase 1 is not closed yet.

This verification surface is the closeout target for the ingest baseline:

- run the golden ingest sweep against `/srv/synapse/test_corpus/golden`
- evaluate the emitted JSON with [`/Users/timsmykov/Desktop/Synapse/scripts/evaluate_ingest.py`](/Users/timsmykov/Desktop/Synapse/scripts/evaluate_ingest.py)
- use [`/Users/timsmykov/Desktop/Synapse/test_corpus/corpus-manifest.json`](/Users/timsmykov/Desktop/Synapse/test_corpus/corpus-manifest.json) as the only canonical manifest
- treat any missing `document_id` from that manifest as a hard failure

Canonical VPS evaluation command:

```bash
PYTHONPATH=src /Users/timsmykov/Desktop/Synapse/.venv/bin/python \
  scripts/evaluate_ingest.py \
  /srv/synapse/repo/data/ingest-golden \
  --manifest /srv/synapse/repo/test_corpus/corpus-manifest.json
```

The evaluation CLI output should always surface:

- `manifest_path`
- `ingest_output`
- `evaluated_document_ids`
- `missing_document_ids` when coverage is incomplete
- keep Phase 1 open until the full selected fixture set clears the gate

Successful full-golden example:

```json
{
  "evaluated_document_ids": [
    "handoyo-2024-meta-analysis",
    "blut-2021-jams",
    "oprea-bra-2025-ebusiness",
    "nguyen-2023-chatbots-frontline",
    "masciari-2024-ai-ethics"
  ],
  "ingest_output": "/srv/synapse/repo/data/ingest-golden",
  "manifest_path": "/srv/synapse/repo/test_corpus/corpus-manifest.json",
  "passed": true,
  "report_count": 5,
  "reports": [
    {
      "document_id": "handoyo-2024-meta-analysis",
      "fixture_file_name": "01-ecommerce-meta-analysis.pdf",
      "passed": true
    }
  ]
}
```

Coverage failure example:

```json
{
  "error": "ingest outputs do not cover the full corpus manifest; missing document_ids: masciari-2024-ai-ethics",
  "evaluated_document_ids": [
    "handoyo-2024-meta-analysis",
    "blut-2021-jams",
    "oprea-bra-2025-ebusiness",
    "nguyen-2023-chatbots-frontline"
  ],
  "ingest_output": "/srv/synapse/repo/data/ingest-golden",
  "manifest_path": "/srv/synapse/repo/test_corpus/corpus-manifest.json",
  "missing_document_ids": [
    "masciari-2024-ai-ethics"
  ],
  "passed": false,
  "reports": []
}
```

Phase 1 can be marked green only when:

- the full selected golden fixture set emits JSON through the canonical ingest path
- the evaluation pass is green for every selected fixture
- the output directory covers the full canonical manifest without omissions
