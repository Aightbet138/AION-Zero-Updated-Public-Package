# AION Zero architecture — v0.1

## Components

- **CLI (`aion.py`)**: explicit local commands; no shell execution or model-generated tool calls.
- **SQLite (`data/aion.sqlite3`)**: record metadata, compressed bodies, verification states, relation links, and revision snapshots.
- **Gzip body store**: compresses text/code record bodies. SHA-256 identifies exact content for deduplication and integrity checks.
- **Search index**: FTS5 indexes small record metadata when compiled into SQLite. `body_terms` stores token frequencies and record IDs, not full plaintext document bodies. Search decompresses candidate records only after matching tokens.
- **Task journal**: task body is structured JSON containing objective, environment, versions, hypotheses, actions, test results, outcome, lessons, reusable solution and event history.
- **Optional local inference**: `ask --model MODEL` passes the question and retrieved context to Ollama at `127.0.0.1:11434`. No hosted endpoint is implemented. Core commands do not need the local model or any network connection.

## Record trust model

New records start `unverified`. The supported statuses are `unverified`, `tested`, `verified`, `rejected`, and `superseded`. A status transition requires written evidence. An unverified item cannot jump straight to verified; it must first be marked tested. A procedure generated from a task is still unverified until a person or later evaluation workflow supplies validation evidence.

Imported documents and task notes are data, not executable instructions. The current app never executes commands or modifies the operating system beyond writing its own data, backup, export, and selected import results.

## Data flow

1. An explicit command adds a record or imports a selected allowlisted text file.
2. Likely secrets and unsafe file types are rejected; hashes identify duplicates.
3. The body is gzip-compressed; metadata and token frequencies are indexed.
4. A query searches indexed terms and metadata, then decompresses only matching candidates.
5. Task outcomes and revisions preserve both failures and improvements for later retrieval.

## Deliberate current limitations

- Search is lexical, not semantic; related concepts with no overlapping terms may be missed.
- A local model is not bundled and no model is trained by the memory engine.
- Secret-pattern detection is best-effort and is not a substitute for review or dedicated secret scanning.
- The code is a local prototype, not a production-certified cybersecurity operator. Use it with non-sensitive lab material first.

## Next design gate

Before adding autonomous system changes, add a local evaluation harness and semantic retrieval, then build a read-only diagnostic agent. Write operations should require least-privilege credentials, sandboxing, an allowlisted tool interface, resource limits, complete audit logs, and rollback tests.
