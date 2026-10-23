# AION Zero — Offline Engineering Memory

**Version:** 0.1 foundation  
**Budget:** $0 in software/license costs  
**Runtime:** Python 3.10+ and SQLite; standard library only  
**Network required at runtime:** No for core memory, ingestion, search, task journaling, backup, restore, export, or diagnostics.

AION Zero is the memory and experience layer for a future engineering agent focused on defensive cybersecurity, cloud engineering, DevOps, Python, and IT. It stores compressed knowledge, keeps task histories, indexes words for quick search, tracks whether procedures have been tested, and preserves prior versions when a record changes.

> Honest boundary: this is not yet a self-learning foundation model or a fully autonomous agent. Without a local model, `ask` retrieves relevant memories but does not reason. An optional Ollama model can provide local reasoning after it has been installed and downloaded. The memory engine never executes generated commands.

## Quick start — Windows

Open PowerShell or Command Prompt in this folder.

```powershell
py --version
py aion.py init
py -m unittest -v
```

Save a lesson and search for it:

```powershell
py aion.py add "Deployment lesson" --kind lesson --category devops --tags "docker,testing" --body "Run a health check and regression tests before calling a deployment successful."
py aion.py search "deployment health check"
py aion.py ask "What deployment checks do we remember?"
```

The default database is `data/aion.sqlite3` next to the script. To place memory somewhere else, set `AION_DATA_DIR` before running the app.

## Quick start — Linux/macOS

```bash
python3 --version
python3 aion.py init
python3 -m unittest -v
python3 aion.py add "Deployment lesson" --kind lesson --category devops --tags "docker,testing" --body "Run a health check and regression tests before calling a deployment successful."
python3 aion.py search "deployment health check"
```

## Main commands

| Goal | Command |
|---|---|
| Initialize/check local database | `py aion.py init` |
| Save a note | `py aion.py add "Title" --body "Text" --kind knowledge --category python` |
| Import text/code from a selected folder | `py aion.py ingest .\learning-notes --category python` |
| Search local memory | `py aion.py search "connection refused"` |
| See one record | `py aion.py show 1` |
| List recent memories | `py aion.py list --limit 30` |
| Record a tested procedure | `py aion.py procedure add "Restart lab service" --prerequisites "Lab VM; access available" --steps "Restart service, then check status" --expected "Service healthy" --risks "Brief interruption" --rollback "Restore previous config"` |
| Start an engineering task | `py aion.py task start "Fix build" --objective "Make tests pass" --environment "Local Windows lab" --versions "Python 3.12" --category devops` |
| Add a hypothesis/action/test | `py aion.py task update 1 --field actions --value "Checked the CI log"` |
| Close the task with evidence | `py aion.py task close 1 --outcome success --validation "All 42 unit tests passed" --lesson "Add regression test for the original bug" --solution "See verified procedure after review"` |
| Mark a record as tested | `py aion.py verify 1 --status tested --evidence "Test suite passed on the stated lab version"` |
| Promote tested record to verified | `py aion.py verify 1 --status verified --evidence "Independent repeat run succeeded" --confidence 0.95` |
| Show record relationships | `py aion.py link 1 2 --relation supports` then `py aion.py related 1` |
| View change history | `py aion.py history 1` |
| Storage stats | `py aion.py stats` |
| Create a checked backup | `py aion.py backup backups\aion.sqlite3` |
| Restore a backup | `py aion.py restore backups\aion.sqlite3 --yes` |
| Export records | `py aion.py export backups\memory.jsonl.gz --gzip` |
| Diagnostics (no network requests) | `py aion.py doctor` |

On Linux/macOS, replace `py` with `python3` in the commands. IDs in examples are placeholders: check the ID printed when you create a record.

## How memory works

- **Compressed bodies:** body content is stored as gzip blobs in SQLite. SHA-256 hashes support deduplication and integrity checks.
- **Search:** the available SQLite FTS5 feature indexes metadata. A separate token/frequency index searches compressed body content without storing a second full plain-text copy of each document. If FTS5 is missing from the local SQLite build, metadata search falls back to a local scan.
- **Persistent task journal:** tasks retain objective, environment, versions, hypotheses, actions, validation results, outcome, lessons, and reusable solution notes.
- **Evidence-based statuses:** `unverified`, `tested`, `verified`, `rejected`, `superseded`. A record cannot jump directly from unverified to verified. Evidence is required for status changes.
- **Revision history:** content/status changes preserve previous compressed bodies and evidence for inspection.
- **Privacy defaults:** the application doesn't send data to a hosted AI service. It uses restrictive local file permissions where supported and screens for some common secret patterns.

## Safe file ingestion

Only ingest folders or files you are authorized to keep. Begin with public documentation, your own notes, and safe code samples. Example:

```powershell
py aion.py ingest .\learning-notes --category python --tags "reference,training-notes" --max-files 200 --max-file-mib 2 --max-total-mib 50
```

The importer allowlists text/code extensions, skips common generated/dependency directories and symlinks, has per-file, total-size and file-count limits, ignores likely secret filenames, rejects binary and invalid UTF-8 content, and rejects some common credential/private-key patterns. These checks are **best-effort, not guaranteed secret detection**. Never import password stores, private keys, API tokens, browser profiles, cloud credential folders, unredacted customer data, or security logs containing sensitive identifiers.

Source files are never modified or deleted. The import process only writes local AION records.

## Offline AI inference (optional, later in setup)

The core memory engine is offline now. AI-generated answers need an inference model; the current optional integration expects Ollama listening on `127.0.0.1:11434`. You must install Ollama and download a model while internet access is available, then the local model can run without a hosted AI API. The program connects to Ollama **only** when you explicitly run a command such as:

```powershell
ollama list
py aion.py ask "Explain the safest way to troubleshoot a failed deployment" --model YOUR_INSTALLED_MODEL_NAME
```

Do not run `ask --model` if you need to guarantee no socket connection is attempted. `doctor` does not contact Ollama or the internet. Model quality and speed depend on your PC's RAM, CPU/GPU, and available storage; downloading a model uses bandwidth and storage even when the software itself is free.

## Backups, exports and recovery

Back up regularly to a separate drive when possible. `backup` uses SQLite's backup API and validates the database. `restore` validates the backup and refuses to overwrite an existing database unless you pass `--yes`; before replacing the active database it makes a timestamped safety copy. JSONL export contains decoded record bodies and must be protected like the original records. Keep backups private.

## Limitations and next milestones

Current v0.1 foundation:
- Compressed local records, duplicate detection and searchable token index
- Safe, bounded text/code ingestion
- Task journals, outcome lessons, record links, status evidence and revisions
- Backup, restore, JSONL export, diagnostics, unit tests
- Optional loopback-only local model integration

Not yet implemented:
- Semantic/vector search or local embeddings
- Model fine-tuning or actual parameter learning
- Autonomous command execution, deployment or system remediation
- Role-based multi-user access, signed audit events or hardened production packaging
- Fully automatic learning from untrusted imported content

The next sensible upgrade is semantic retrieval over a local embedding model, followed by an evaluated read-only diagnostic agent. Tool execution should come only after isolated execution, explicit permissions, audit logs, rate limits, and rollback are designed and tested.

## Tests

Run the regression suite from this directory:

```powershell
py -m unittest -v
```

Tests create their own temporary databases and synthetic sample data. They cover persistence, deduplication, compression, search, evidence-gated status changes, task history, ingestion defenses, symlink rejection, backup/restore, export, and proof that the core path doesn't attempt network connections.
