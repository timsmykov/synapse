# Synapse Test Corpus Source

This document is the source of truth for the real golden PDF set used by Synapse.

## Canonical Source

The real source PDFs currently live outside the repo at:

- `/Users/timsmykov/Desktop/Статьи для теста`

This path is the operator-owned source folder on the Mac workstation.

## Rule

- Do not treat `test_corpus/` inside the repo as the canonical source of the real PDFs.
- `test_corpus/` in the repo is for manifests, mirrors, fixture metadata, and test-side artifacts only.
- The actual research PDFs should be selected from `/Users/timsmykov/Desktop/Статьи для теста` and then synced to the server-side corpus location for execution.

## Canonical Manifest

- [`/Users/timsmykov/Desktop/Synapse/test_corpus/corpus-manifest.json`](/Users/timsmykov/Desktop/Synapse/test_corpus/corpus-manifest.json) is the only canonical manifest for the active golden baseline.
- [`/Users/timsmykov/Desktop/Synapse/test_corpus/corpus-manifest.template.json`](/Users/timsmykov/Desktop/Synapse/test_corpus/corpus-manifest.template.json) is historical scaffolding only and must not drive evaluation defaults or Phase 1 signoff.
- [`/Users/timsmykov/Desktop/Synapse/scripts/evaluate_ingest.py`](/Users/timsmykov/Desktop/Synapse/scripts/evaluate_ingest.py) must evaluate against the canonical manifest and fail when the output set does not cover every selected fixture.

## Server-First Policy

- Mac stores the source PDFs.
- Server runs ingest, tests, and runtime flows.
- CI must not depend on the Mac-local absolute path.

## Selected Starter Baseline

The first operational baseline uses these five source PDFs:

- `Handoyo (2024) - Trust, Risk, Security in E-commerce Meta-analysis.pdf`
- `Blut, M., et al. (2021) - Journal of the Academy of Marketing Science.pdf`
- `Oprea & Bra (2025) - AI Game-Changer in E-Business.pdf`
- `Nguyen et al. (2023) - Chatbots Anthropomorphism Customer Experience.pdf`
- `Masciari et al. (2024) - AI Recommendation Systems and Ethics.pdf`

These are mapped to stable mirrored names in [`/Users/timsmykov/Desktop/Synapse/test_corpus/corpus-manifest.json`](/Users/timsmykov/Desktop/Synapse/test_corpus/corpus-manifest.json).
The repo-side manifest and [`/Users/timsmykov/Desktop/Synapse/scripts/sync_test_corpus.sh`](/Users/timsmykov/Desktop/Synapse/scripts/sync_test_corpus.sh) are the authoritative bridge into the server corpus.
The current server copy at `/srv/synapse/test_corpus/golden` was verified on 2026-04-08.

## Why These Five

They give a solid first server-side ingest baseline for:

- citation-heavy review and meta-analysis papers
- multi-column journal layouts
- table extraction on long-form academic PDFs
- one methods-heavy paper with likely formulas or formal notation
- one likely complex-table or taxonomy-style review article

## Current Gap

This starter baseline is not yet strong for:

- formula-heavy scientific PDFs
- biology-style figure panel layouts
- clinical RCT tables with more specialized structure

That second corpus wave should be added after the first ingest pass is stable.

## Next Step

1. Run the first server-side ingest pass on `/srv/synapse/test_corpus/golden`.
2. Evaluate the resulting JSON with [`/Users/timsmykov/Desktop/Synapse/scripts/evaluate_ingest.py`](/Users/timsmykov/Desktop/Synapse/scripts/evaluate_ingest.py) against the canonical manifest.
3. Treat any missing golden JSON output as a hard failure, not as a partial green.
4. Refine `expected_artifacts` from provisional lower bounds to measured thresholds.
5. Add a second corpus wave for formula-heavy and non-marketing scientific PDFs.

For the exact VPS command shape and the canonical success/failure JSON examples, use [`/Users/timsmykov/Desktop/Synapse/docs/phase-1-verification.md`](/Users/timsmykov/Desktop/Synapse/docs/phase-1-verification.md).
