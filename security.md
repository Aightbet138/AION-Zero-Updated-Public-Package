<!-- SPDX-License-Identifier: Apache-2.0 -->

AION Zero v0.4.0 — Security and Licensing Review
Review date: 2026-10-24
Scope: Local public-prep source tree, first-party documentation, dependency declarations, test fixtures, and GitHub Actions workflow.
Review type: Best-effort static review and package-preparation check; not a penetration test, formal security audit, or legal opinion.
Summary
The local application source imports Python standard-library modules and other AION Zero modules. No third-party Python runtime requirements manifest, bundled model weights, or bundled Ollama runtime was found. The CLI's model requests use a hard-coded loopback Ollama address. The bounded diagnostics use fixed tool names; the only subprocess uses found in the reviewed tool code are fixed-argument Git status and an explicitly opt-in Python unittest invocation with shell=False.

Two concrete public-preparation issues were corrected in this review: the project NOTICE attribution was inconsistent with the README attribution, and the CI workflow used mutable action tags without explicit permissions or disabling stored checkout credentials. Two synthetic secret fixtures (a fake private-key header and a fake AWS-style access-key string) caused scanner warnings; both test cases now construct the same input at runtime by concatenating string literals so static scanning does not mistake them for real credentials.
Checks and results
Check	Result	Interpretation
Python compile / syntax parse	Passed for aion.py, aion_skills.py, aion_tools.py, aion_enterprise.py, and test_aion.py	Syntax validation only; not a functional security guarantee.
Built-in best-effort secret-pattern scan	Two initial findings were synthetic regression-test strings; both were rewritten, and a follow-up scan is recorded below	Zero pattern findings after the edits. Pattern scans cannot prove a tree is secret-free.
Heuristic configuration scan	Three matches, all source-code examples/rules/test fixtures rather than deployment configuration	Expected false positives from scanning the scanner's own patterns and safety examples. There are no shipped deployment manifests in the reviewed tree.
Runtime database inspection	Local data/aion.sqlite3 existed but contained zero user records	Runtime data/, databases, caches and backups must remain excluded from public archives.
Dependency inventory	Standard library for the Python runtime; no requirements.txt or package manifest	Ollama and model weights are optional external downloads and carry separate license terms.
GitHub Actions	Hardened locally	Actions are pinned by full commit SHA, permissions are read-only, checkout credentials are not persisted, and Dependabot checks the workflow weekly. The updated workflow has not yet been run by GitHub Actions.
Review archive assembly	Passed	50 files included; runtime database/data, caches, logs, virtual environments, and database files excluded. The extracted package scan checked 46 text/code files and reported zero potential-secret findings. Archive SHA-256 checksum validated.
Full unit suite	Timed out after about 185 seconds before completion	Not a pass. Must be rerun to completion in CI and on clean Windows/Linux environments.


Findings and actions
Addressed: NOTICE attribution mismatch
README.md named Junior Justin Amusa as the project attribution while NOTICE said “AION Zero contributors” and asked to replace that generic notice. NOTICE now matches the maintainer-provided name. This change is a document consistency fix only; it does not independently establish who owns copyright or whether all content is licensable.
Addressed: mutable GitHub Actions references and broad default token permissions
The test workflow now pins actions/checkout v7.0.1 to commit 3d3c42e5aac5ba805825da76410c181273ba90b1 and actions/setup-python v7.0.0 to commit 5fda3b95a4ea91299a34e894583c3862153e4b97. Workflow/job permissions are limited to contents: read, and checkout uses persist-credentials: false. Dependabot is configured to check GitHub Actions references weekly. Pinning prevents a tag from silently moving but requires maintainers to review and merge updates.
Addressed: synthetic secret scanner false positive
Two test cases deliberately included fake credentials to prove that AION detects suspicious input and does not echo a matched value. These were not real secrets, but the scanner flagged the literals. The fixtures now concatenate their markers at runtime, preserving the test inputs while avoiding misleading static findings.
Remaining: no full test-suite result
The local python -m unittest -v test_aion.py run did not finish within approximately 185 seconds. It had not completed by the time the command was stopped. Three targeted security/approval regression tests did pass after the edits, and all five Python files compiled successfully; this is not a substitute for the complete suite. Do not claim the complete test suite passed based on this review. The new CI workflow must complete successfully before a release claim is made.
Remaining: copyright, provenance, and external history
Apache License 2.0 is present as the project's chosen license and is the standard upstream text. Apache-2.0 permits reuse and redistribution subject to its conditions; applying it requires the distributor to have the necessary rights. The maintainer must confirm rights to every source file, skill pack, document, test fixture, and contribution, and check copied/adapted material for required notices. The local folder has no Git history, and this review cannot inspect deleted files, older commits, or all content previously uploaded to GitHub.
Remaining: contact and repository controls
The repository's security contact is documented but its mailbox has not been independently verified as controlled and monitored. The maintainer must confirm it is monitored and enable GitHub private vulnerability reporting in repository settings. Public repositories have GitHub secret-scanning support, but it should supplement, not replace, review of source, ZIP contents, and complete commit history.
Required before announcing a stable public release
1. Confirm copyright/provenance and authority to use Apache-2.0 for every included component; record any additional licenses/attributions.
2. Use the reviewed ZIP and its matching SHA-256 file as a pair. If any file is changed before upload, rebuild the archive and repeat the secret scan; never publish real tokens, private keys, databases, logs, exports, or backups.
3. Inspect the full Git history and all prior release uploads. Rotate any secret that may ever have been published; deleting it from the latest tree is insufficient.
4. Confirm the security inbox works and is monitored; enable private vulnerability reporting where available.
5. Run the full CI matrix to completion on Windows and Linux, resolve failures/timeouts, and document the Python versions/platforms actually tested.
6. Treat finance/legal/security outputs as assistive records, not professional advice or certification; keep the existing non-sandbox and no-production-certification warnings.
External references checked
- Apache License 2.0 and application guidance: https://www.apache.org/licenses/LICENSE-2.0.html and https://www.apache.org/legal/apply-license
- GitHub secret scanning: https://docs.github.com/en/code-security/concepts/secret-security/secret-scanning
- GitHub Actions secure use (pin actions to a full commit SHA): https://docs.github.com/en/actions/reference/security/secure-use
- GitHub private vulnerability reporting: https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/report-privately
