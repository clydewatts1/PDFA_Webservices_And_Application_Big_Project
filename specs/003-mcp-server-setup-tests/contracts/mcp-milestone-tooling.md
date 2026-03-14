# MCP Milestone Tooling Contract

## Purpose
Define review contracts for MCP configuration, tool responses, and test-runbook verification for milestone acceptance.

## Scope
- Canonical MCP configuration document: `WB-Workflow-Configuration.yaml`
- Tools: `get_system_health`, `user_logon`, `user_logoff`
- Table CRUD tools for: Workflow, Role, Interaction, Guard, InteractionComponent
- Test runbook including required `npx @modelcontextprotocol/inspector` and manual SQL verification steps

## Contract Rules

### 1) Configuration Contract
- MCP configuration source is YAML and canonical filename is `WB-Workflow-Configuration.yaml`.
- Database connectivity values are sourced from `.env` aligned with `env.example`.
- Mock auth user map is declared in YAML.

### 2) Health Tool Contract
`get_system_health` response must include:
- `health_status` in {`CONNECTED`,`DISCONNECTED`,`FAILED`,`INITIALIZING`,`DEAD`}
- `health_status_description` (required)
- Error detail fields when status is `FAILED` or `DEAD`

### 3) Auth Tool Contract
- `user_logon` accepts `username` and `password`.
- `user_logon` statuses: `SUCCESS`, `DENIED`, `ERROR`.
- `user_logoff` accepts `username`.
- `user_logoff` statuses: `SUCCESS`, `ERROR`.
- Error message field is required for error outcomes.

### 4) CRUD Tool Contract
For each in-scope table, expose:
- `create_[table]`
- `get_[table]`
- `list_[table]s`
- `update_[table]`
- `delete_[table]`

Shared constraints:
- Normalized result envelope includes `status` (`SUCCESS`|`ERROR`) and `status_message`.
- `get/update/delete` require primary key input.
- `list` supports optional `limit`/`offset`.

### 5) Test Runbook Contract
The test document must include:
- MCP + DB setup steps.
- Required command path using `npx @modelcontextprotocol/inspector`.
- End-to-end tool verification sequence (health, auth, one CRUD lifecycle minimum).
- Manual direct database verification using `sqlite3` as primary path.
- Optional equivalent `psql` queries for PostgreSQL users.

## Response Envelope Examples

### `get_system_health` (success)

```json
{
  "status": "SUCCESS",
  "status_message": "Health check completed",
  "health_status": "CONNECTED",
  "health_status_description": "Database connection is healthy",
  "health_status_error": "",
  "health_status_error_detail": ""
}
```

### `user_logon` (denied)

```json
{
  "status": "DENIED",
  "status_message": "Invalid username or password",
  "ErrorMessage": "Credentials denied",
  "username": "reviewer"
}
```

### CRUD Tool (generic success)

```json
{
  "status": "SUCCESS",
  "status_message": "workflow.create completed",
  "WorkflowName": "SampleWF",
  "DeleteInd": 0
}
```

## Review Output Schema

```json
{
  "check_date": "YYYY-MM-DD",
  "overall_result": "pass|fail",
  "results": {
    "config_contract": "pass|fail",
    "health_tool_contract": "pass|fail",
    "auth_tool_contract": "pass|fail",
    "crud_tool_contract": "pass|fail",
    "runbook_contract": "pass|fail"
  },
  "evidence_paths": [],
  "open_issues": []
}
```

## Failure Conditions
- Canonical config file naming not satisfied.
- Missing required tools or status fields.
- CRUD set incomplete for in-scope tables.
- Missing required inspector command path.
- Missing direct manual SQL verification instructions.

## Non-Goals
- Production-grade authentication/security implementation.
- Schema redesign outside current scope.
- Changes to three-tier architectural boundaries.
