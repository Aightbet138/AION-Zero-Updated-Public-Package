AION Zero v0.4.0 — Offline Engineering Intelligence
AION Zero is an experimental, offline-first engineering assistant designed to retain technical knowledge, retrieve previous experience, organize task history, and support a limited set of approved local diagnostics.
Project status: prototype / public-preparation build. This is a development foundation, not a production-certified or fully autonomous AI system.

Download
[**Download the AION Zero v0.4.0 Public-Prep package (ZIP)**](./AION_Zero_v0.4.0_Public_Prep_Junior_Justin_Amusa_Profile.zip)

The archive contains the Python code, tests, skill packs, and supporting project documentation. Extract it and open a terminal in the extracted aion_zero directory before running commands.
Verify the download
SHA-256:
de5fed8c391abd18b2cf0838ca4820267db76461bdbb082bfdc22fba71290703
Windows PowerShell:
Get-FileHash .\AION_Zero_v0.4.0_Public_Prep_Junior_Justin_Amusa_Profile.zip -Algorithm SHA256
Linux:
sha256sum AION_Zero_v0.4.0_Public_Prep_Junior_Justin_Amusa_Profile.zip
Compare the calculated hash with the value above.
What it currently includes
- Persistent local memory: stores knowledge and task history in SQLite, with compressed record bodies and duplicate detection.
- Retrieval: keyword search by default; optional semantic and hybrid retrieval using locally hosted embeddings.
- Engineering skill packs: reusable workflows and instructions for Python, Linux/IT, DevOps, networking, cloud, databases, reliability, and defensive cybersecurity.
- Task journal and evidence states: records objectives, actions, outcomes, lessons, and verification evidence.
- Backups and export: tools for backing up, restoring, and exporting local records.
- Bounded diagnostics and audit history: supported, allowlisted checks with approval gates and recorded outcomes.
- Operational records: basic finance and bookkeeping helpers, bill tracking, budget records, and a compliance deadline register.
- Experience statistics: a simple record of past tool outcomes; it is not a general-purpose learning model.
Requirements
- Python 3.10 or newer.
- SQLite support included with the Python installation.
- No third-party Python packages are required for the basic memory workflows.
- Optional: Ollama and separately downloaded models for local AI inference and semantic embeddings.
Quick start
Windows
Open PowerShell in the extracted aion_zero directory:
py --version
py aion.py init
py aion.py doctor
py aion.py skills list
py aion.py skills seed
py -m unittest -v
Save and search a first note:
py aion.py add "Deployment lesson" --kind lesson --category devops --tags "testing,docker" --body "Run health checks and regression tests before declaring a deployment successful."
py aion.py search "deployment health check"
Linux / macOS
python3 --version
python3 aion.py init
python3 aion.py doctor
python3 aion.py skills list
python3 aion.py skills seed
python3 -m unittest -v
The default memory database is data/aion.sqlite3 within the project directory. Set AION_DATA_DIR to use a different data location.
Optional local AI features
Core memory, keyword search, task journaling, backup, restore, and supported diagnostics do not need an AI model or runtime internet access. AI-generated planning and semantic search require a local Ollama service and models already downloaded to your computer.

For semantic retrieval, install Ollama separately, then run:
ollama pull all-minilm
py aion.py embeddings index --model all-minilm
py aion.py search "the service keeps failing" --mode semantic --embedding-model all-minilm
Use python3 instead of py on Linux/macOS. For AI-generated answers, download a chat model compatible with your hardware and pass its installed name to the relevant --model option. Model quality and speed depend on your computer and model choice. Model weights are not bundled in this repository archive.
Safety, privacy, and limitations
- AION stores memory locally by default and does not send core memory workflows to a hosted AI API. Optional AI features call a local Ollama endpoint.
- Ingestion secret checks are best-effort; they cannot guarantee detection of every credential or sensitive record. Do not ingest private keys, passwords, API tokens, cloud credentials, or unredacted customer data.
- The local planner is not authorized to execute arbitrary model-written shell commands. Diagnostic execution is limited to supported tools and approval-gated workflows.
- The optional test runner executes project code with your operating-system user's permissions. It is not a sandbox; only run code you trust.
- Finance features organize records and perform basic calculations; they do not initiate payments or connect to banks. The compliance register tracks dates and evidence; it does not provide legal advice or certify compliance.
- The experience twin records simple empirical statistics. AION does not independently train or upgrade its foundation model from experience.
- This release is not production-hardened or certified for security, accounting, legal, or regulatory compliance.
Read the included OFFLINE_SETUP.md, ARCHITECTURE.md, SECURITY.md, PRIVACY.md, LEGAL_AND_FINANCIAL_DISCLAIMER.md, and THIRD_PARTY_NOTICES.md for more detail.
Project documentation
The package includes additional documentation covering architecture, offline setup, security reporting, privacy, contribution guidelines, support, the changelog, build notes, licensing, third-party notices, and publication readiness. These files are inside the downloaded ZIP archive.
Reporting issues and security concerns
- General bugs and feature requests: GitHub Issues
- Suspected security vulnerabilities: deez2nutsmaster@gmail.com. Please do not include passwords, live secrets, or personal data in a report. See SECURITY.md in the archive for reporting guidance.
License
The repository includes an Apache License 2.0 license file. Review NOTICE and THIRD_PARTY_NOTICES.md in the archive for attribution and third-party information. Confirm you have the rights to redistribute all included material before creating further distributions. Optional Ollama software and model weights have separate terms.
Maintainer
Junior Justin Amusa
GitHub: @Aightbet138 · LinkedIn · ORCID · X
Roadmap direction
The development direction is to make AION's workflows more reproducible: recall relevant experience, propose a bounded plan, perform permitted actions, verify results, and save evidence for future tasks. The next milestones should prioritize a clean installation, automated testing, safer diagnostics, clearer documentation, and measured results before expanding automation.
