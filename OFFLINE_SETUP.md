# Offline operation notes

AION Zero's core works locally with Python and SQLite. It does not need a cloud account, hosted API, or network access for database creation, local search, import, task journaling, compression, diagnostics, backup, restore, or export.

## Strictly offline core

Use commands such as:

```powershell
py aion.py doctor
py aion.py search "previous deployment issue"
py aion.py task start "Investigate Python traceback" --objective "Find root cause" --environment "local test machine"
```

Do not add `--model` to `ask` if no socket connection is acceptable. AION only opens a loopback connection when a user explicitly requests a local model with `ask --model MODEL_NAME`.

## Optional local inference

To get generated answers while remaining independent of hosted APIs, install Ollama and download a model while online. Verify that the model appears in `ollama list`, then disconnect and try `py aion.py ask "question" --model MODEL_NAME`. Ollama and the model are optional: without them, AION still stores and retrieves memory but does not independently reason over it.

No particular model is mandated. Choose based on actual RAM/CPU/GPU limits and available disk space. Model downloads are often multiple gigabytes, so the zero-cost goal is zero software/license cost, not zero bandwidth or electricity cost.

## Security note

Local-only does not automatically mean safe. Restrict OS user access to the data folder, back it up, don't import secrets, and don't let an AI execute generated shell commands without a later security design involving least privilege, isolation, validation and rollback.
