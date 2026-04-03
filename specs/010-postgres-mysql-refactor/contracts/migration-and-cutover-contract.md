# Contracts: Migration and Cutover Contract

Feature: 010-postgres-mysql-refactor  
Date: 2026-04-03

## MCP Tool Contracts

No JSON-RPC tool shape changes are introduced by this feature.

Unchanged contract expectations:
- Existing method names remain stable.
- Existing request and response payload structures remain stable.
- Existing error envelope conventions remain stable.

## HTTP/SSE Contracts

No Quart route payload or SSE stream schema changes are introduced.

Boundary contract remains:
- Quart communicates with MCP over HTTP only.
- No direct database contract is exposed to web-tier routes/pages.

## Migration Execution Contract

Required operational contract for this feature:
- Baseline-to-head migration must execute successfully on MySQL.
- Failure to migrate is a release-blocking condition.
- Migration validation evidence must be captured and reviewable.

Validation fields (minimum):
- revision_start
- revision_end
- executed_at_utc
- status (passed or failed)
- failure_reason (required when failed)

## Test Target Contract

Required target for validation suites:
- Contract tests execute on MySQL.
- Integration tests execute on MySQL.
- SQLite is not a valid substitute for contract/integration sign-off in this feature.
- Any contract or integration run that uses SQLite must be treated as non-sign-off diagnostic coverage only.

## Data Cutover Contract

Cutover data rule:
- No historical PostgreSQL backfill into MySQL for this feature.
- MySQL starts from initialized schema baseline.
- Only post-cutover records are expected in MySQL.

## Rollback Governance Contract

Rollback rule:
- Rollback to PostgreSQL is permitted only within 24 hours from cutover start.
- Rollback requires explicit trigger criteria and approver.
- After window expiry, operational mode is fix-forward on MySQL unless rollback was initiated in-window.

Minimum rollback decision fields:
- cutover_start_utc
- rollback_deadline_utc
- decision_time_utc
- trigger_reason
- approved_by
- outcome (rollback_executed or fix_forward)

## Environment Variable Contract

Required runtime variable:
- DB_URL must point to MySQL runtime target for contract/integration and cutover validations.

Expected format:
- mysql+pymysql://user:password@host:3306/dbname?charset=utf8mb4

Legacy PostgreSQL URLs may exist only for rollback readiness during the active rollback window and must not be the default runtime target after cutover completion.
