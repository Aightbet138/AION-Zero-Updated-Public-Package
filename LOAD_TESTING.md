# AION SaaS load testing (1,000+ simulated tenant identities)

SPDX-License-Identifier: Apache-2.0

This is a workload harness, not a capacity guarantee. Run only against a dedicated staging environment containing synthetic data. Never point Locust at production or real customer tenants. A 1,000-user test is not complete evidence by itself: save latency, errors, throughput, DB-pool wait, queue age, CPU/memory, cloud API throttles, test settings and the build digest.

## Install and generate 1,000 synthetic identities

Use a dedicated virtual environment, then install the enterprise dependencies and Locust:

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS:
source .venv/bin/activate
python -m pip install -r requirements-enterprise.txt -r requirements-loadtest.txt
python loadtests/generate_tokens.py --count 1000 --output-dir /tmp/aion-loadtest
```

On Windows, choose a private output folder (for example `%TEMP%\\aion-loadtest`) instead of `/tmp/aion-loadtest`. The generator creates 1,000 synthetic `tenant_id`/`sub` identities and an ephemeral RSA key. Only the public JWKS and bearer tokens are written; the signing private key is never saved. Tokens expire after 90 minutes by default. Treat `tokens.json` like a secret and delete the directory after the test.

## Start an isolated API under a test issuer

The load-test issuer is synthetic and is not a real identity provider. The API accepts its loopback-only HTTP JWKS endpoint only while `AION_ENV` is not production and `AION_ALLOW_INSECURE_OIDC_TESTS=1` is explicitly enabled.

1. Create a disposable PostgreSQL database, initialize it with `deploy/postgres/init.sql`, create the non-owner API/worker roles, and run `python aion_migrate.py apply` using a migration-only DSN.
2. Start the fake JWKS server on the same host as the API:

```bash
python loadtests/serve_jwks.py --jwks-file /tmp/aion-loadtest/jwks.json --port 8765
```

3. In a separate terminal on that same host, configure a local test API. The `AION_DATABASE_URL` must be the non-superuser API role DSN, not a production DSN:

```bash
export AION_ENV=development
export AION_ALLOW_INSECURE_OIDC_TESTS=1
export AION_DATABASE_URL='postgresql://aion_app:TEST_ONLY_PASSWORD@127.0.0.1:5432/aion_loadtest'
export AION_OIDC_ISSUER='https://aion-loadtest.invalid/'
export AION_OIDC_AUDIENCE='aion-enterprise-api'
export AION_OIDC_JWKS_URL='http://127.0.0.1:8765/jwks.json'
export AION_TENANT_CLAIM=tenant_id
export AION_ROLES_CLAIM=roles
export AION_RATE_LIMIT_PER_MINUTE=120
uvicorn aion_api:app --host 127.0.0.1 --port 8080 --workers 2
```

On Windows PowerShell, use `$env:NAME='value'` for each environment variable and `py -m uvicorn ...`. This test mode is for a localhost-only test service. Never set the insecure OIDC test flag in a deployed environment.

## Run a ramp test, then a soak test

In another terminal, set the path to the generated tokens file and run:

```bash
export AION_LOAD_TEST_TOKENS_FILE=/tmp/aion-loadtest/tokens.json
export AION_LOAD_TEST_EXPECTED_TENANTS=1000
locust -f loadtests/locustfile.py --host http://127.0.0.1:8080 \
  --users 1000 --spawn-rate 25 --run-time 10m --headless \
  --csv loadtests/results_1000_tenants --html /tmp/aion-loadtest/report.html
```

This performs authenticated identity checks, tenant-scoped work-request listing, and synthetic work submissions under one distinct tenant token per simulated user on a single Locust process. Use 100, 250, 500, then 1,000 users in separate runs to identify where throughput and tail latency degrade. For soak testing, run at the expected peak load for at least 60 minutes, with the worker pool running and synthetic jobs flowing. Delete reports if they contain any sensitive deployment metadata before sharing them.

## Interpret the results

No numerical performance promise is made before a run. Record at minimum:

- Request rate and completed requests/second by endpoint.
- p50, p95 and p99 latency; error counts and status-code mix, especially `429` and `5xx`.
- PostgreSQL CPU, active/idle connections, connection-pool wait/timeout, locks, slow queries, rate-limit table contention and storage I/O.
- Queue depth, oldest queued age, retry/dead-letter count, lease expirations, worker CPU/memory and worker concurrency.
- API/worker replica counts, CPU/memory limits, database size, region, instance classes, client wait time, request sizes, code/image digest, and test duration.

A release gate must define acceptable thresholds before running the test. Do not infer “supports 1,000 customers” from 1,000 virtual users alone. Repeat tests after changes to OIDC verification, PostgreSQL schema, rate limits, tenant policy, worker concurrency, model inference, cloud adapters, or infrastructure.

## Guardrails

- Test data is synthetic; do not include production data or credentials.
- Keep the local fake OIDC endpoint bound to loopback only.
- Do not enable cloud adapters or provide real cloud credentials during the baseline API capacity test.
- Do not run external-mutation tests; load requests are non-sensitive and worker outputs remain human-review-only.
- Do not commit generated tokens/JWKS/reports. `.gitignore` excludes the expected artifact paths.
- Shut down the API/JWKS processes and delete the token directory after the run.
