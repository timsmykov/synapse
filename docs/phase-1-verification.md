# Phase 1 Verification

Phase 1 is not closed yet.

This verification surface is the closeout target for the ingest baseline:

- run the golden ingest sweep against `/srv/synapse/test_corpus/golden`
- evaluate the emitted JSON with [`/Users/timsmykov/Desktop/Synapse/scripts/evaluate_ingest.py`](/Users/timsmykov/Desktop/Synapse/scripts/evaluate_ingest.py)
- use [`/Users/timsmykov/Desktop/Synapse/test_corpus/corpus-manifest.json`](/Users/timsmykov/Desktop/Synapse/test_corpus/corpus-manifest.json) as the only canonical manifest
- treat any missing `document_id` from that manifest as a hard failure

The evaluation CLI output should always surface:

- `manifest_path`
- `ingest_output`
- `evaluated_document_ids`
- `missing_document_ids` when coverage is incomplete
- keep Phase 1 open until the full selected fixture set clears the gate

Phase 1 can be marked green only when:

- the full selected golden fixture set emits JSON through the canonical ingest path
- the evaluation pass is green for every selected fixture
- the output directory covers the full canonical manifest without omissions
