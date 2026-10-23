# Changelog

## v0.1 — Memory foundation

- Local SQLite storage with gzip-compressed record bodies and SHA-256 duplicate detection.
- Metadata FTS5 plus a compact token-frequency index for searching compressed record bodies.
- Safe, bounded ingestion of allowlisted UTF-8 text/code files with symlink, binary and best-effort secret screening.
- Structured engineering task journaling and reusable procedure records.
- Evidence-gated verification statuses, record relationships and revision history.
- Checked database backup/restore, JSONL export, diagnostics, and standard-library regression tests.
- Optional inference integration explicitly restricted to a local Ollama loopback endpoint.
- Migration support for the earlier AION Zero starter schema.
