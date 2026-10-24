# AION SaaS policy control map (design intent, not certification)

SPDX-License-Identifier: Apache-2.0

| Control area | Current design/evidence | Remaining assurance task |
|---|---|---|
| Identity and authentication | OIDC RS256/JWKS validation; issuer/audience/expiry/subject checks; role mapping | Test real IdP key rotation, revocation expectations, MFA and account lifecycle |
| Tenant isolation | Transaction-local tenant setting, forced PostgreSQL RLS, tenant-scoped SQL, hostile cross-tenant integration tests | Run tests on the production database service; review all schema changes and backup/export paths |
| Authorization | Route-level roles, tenant administrator for cloud bindings, explicit status transitions | Independent authorization matrix review and negative tests for every new route |
| Durable work | PostgreSQL queue, atomic request+job insert, lease, bounded retries, dead-letter, idempotency | Test process kill, database failover, poison jobs and multi-worker race conditions |
| Cloud credentials | Per-tenant AWS role/external ID, Azure tenant/subscription/app and tenant-namespaced vault ref, GCP project/service-account impersonation; connection config lookup is job-lease-scoped | Real provider account tests, external-ID trust policy validation, least-privilege IAM and secret-manager namespace review |
| Secret management | Secret references validated for tenant namespaces; no raw cloud credential input | Validate vault policy, deletion, rotation and break-glass access in staging |
| API abuse controls | Shared DB-backed per-user/tenant rate counter, body limit, security headers | Add ingress/WAF limits, distributed attack controls, quota/billing integration and noisy-neighbour tests |
| Audit and logs | Append-only audit table; structured worker logs intended to avoid payload/credential values | Verify immutable export, retention, alerting, redaction and least-privilege log access |
| Backup/recovery | Encrypted age-based backup helper; checksums; isolated restore constraints | Run scheduled backup/restore drills and document actual RPO/RTO |
| Software supply chain | Pinned GitHub Actions by SHA, optional Dependabot, immutable image deployment pattern | Add SAST/SCA/container/image signing and artifact provenance for target release process |
| Availability and performance | Bounded API/worker DB pools and wait queues, durable worker process, authenticated queue metrics, 1,000-identity Locust workload generator | Execute 1,000+ tenant load test, soak/failover tests, capacity plan and measured SLOs; harness is not capacity evidence |
| Privacy and data retention | Privacy and security docs; collect only supported workflow data | Complete data inventory, DPAs, subprocessors, region/residency, retention/deletion and privacy impact assessment |
| Human oversight | Cloud inventory read-only; models do not execute generated commands; sensitive actions gated | Define approval UX, separation of duties, emergency stop and customer-specific risk controls |
| Incident management | Runbook and documented containment steps | Assign on-call owners, test notification channels, rehearse incident and counsel-led notification decision |

## External framework alignment

This map can support a scoped gap assessment against OWASP ASVS/API Security Top 10, NIST CSF, ISO/IEC 27001, SOC 2, and applicable privacy/security laws. It does not establish conformity. Framework version, scope, system boundary, customer contract and auditor requirements must be selected explicitly. Only an independent assessment/audit can substantiate certifications or audited attestations.
