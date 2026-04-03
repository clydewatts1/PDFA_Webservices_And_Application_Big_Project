# Quickstart: Continue PostgreSQL to MySQL Refactor

Feature: 010-postgres-mysql-refactor

This runbook validates migration completion according to clarified scope:
- MySQL-only contract and integration validation
- No historical PostgreSQL data backfill
- 24-hour rollback window

## 1) Prerequisites

- Python 3.11+ virtual environment activated
- Reachable MySQL 8.x instance
- Legacy PostgreSQL kept available for rollback window only
- Required environment variables set for MCP and web tiers

## 2) Configure Environment

Set MySQL runtime URL:

```env
DB_URL=mysql+pymysql://user:password@host:3306/pdfa_workflow?charset=utf8mb4
DEFAULT_ACTOR=local_dev
MCP_CONFIG_PATH=WB-Workflow-Configuration.yaml
MCP_SERVER_URL=http://127.0.0.1:5001
CUTOVER_WINDOW_START_UTC=2026-04-03T12:00:00Z
ROLLBACK_WINDOW_HOURS=24
CUTOVER_DECISION_OWNER=on-call-reviewer
```

Confirm no PostgreSQL runtime URL is active in the shell and do not leave `.env` pointed at `sqlite:///./local.db` for contract/integration sign-off.

## 3) Apply Baseline-to-Head Migrations on MySQL

```powershell
python -m alembic -c database/alembic.ini upgrade head
```

Expected outcome:
- Command completes without dialect or DDL errors.
- Current and `_Hist` table pairs exist for all seven workflow entities.

## 4) Validate MCP Runtime on MySQL

Start MCP runtime in HTTP mode:

```powershell
python -m mcp_server.src.server --transport http --host 127.0.0.1 --port 5001
```

Run health checks and core workflow operations. Expected outcome:
- Database health reports success.
- Core create/update flows preserve temporal behavior.

## 5) Execute MySQL-Only Contract and Integration Suites

Run designated contract tests:

```powershell
pytest mcp_server/tests/contract -v --tb=short
```

Run designated integration tests:

```powershell
pytest mcp_server/tests/integration -v --tb=short
```

Expected outcome:
- Suites pass against MySQL.
- No SQLite fallback for contract/integration validation paths.

## 6) Cutover Without Historical Backfill

Cutover rule for this feature:
- Do not import pre-cutover PostgreSQL records into MySQL.
- Treat MySQL baseline schema as the starting data state.
- Accept only post-cutover writes in MySQL.

## 7) Start Rollback Window

At cutover start, declare:
- rollback_window_start_utc
- rollback_window_end_utc (start + 24h)
- on-call approver and decision owner

Rollback is allowed only within this 24-hour window if validation criteria fail.

## 8) Rollback Criteria

Trigger rollback when any of the following is true within window:
- Migration validation failure
- MCP health-check failure under expected load/profile
- Contract or integration validation failure
- Incident owner manual abort with documented reason

If rollback is not triggered by window end, switch to fix-forward posture on MySQL.

## 9) Evidence Capture

Record the following in project evidence logs:
- Migration command output and revision range
- Contract/integration MySQL test output
- Cutover window start/end timestamps
- Rollback decision (or commit decision) and approver

## 10) Handover Checklist

- `.env` or shell environment points to MySQL with `mysql+pymysql://...`.
- `CUTOVER_WINDOW_START_UTC`, `ROLLBACK_WINDOW_HOURS`, and `CUTOVER_DECISION_OWNER` are set before MCP startup.
- Baseline-to-head migration has been run successfully on MySQL.
- `pytest mcp_server/tests/contract -v --tb=short` passes on MySQL.
- `pytest mcp_server/tests/integration -v --tb=short` passes on MySQL.
- Rollback decision owner has recorded either `rollback_executed` or `fix_forward` before or at rollback deadline.
