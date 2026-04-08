# Data Model: Full Stack WSGI Migration

## Overview

This feature does not introduce new persistence tables. The relevant entities are runtime and interface models that govern how the Flask web tier and Flask MCP wrapper interact while preserving existing MCP-owned database behavior.

## Entities

### 1. McpWrapperConfig

- Purpose: Runtime configuration for the MCP Flask WSGI wrapper.
- Fields:
  - `db_url`: SQLAlchemy connection URL used only by the MCP tier.
  - `mcp_config_path`: path to `WB-Workflow-Configuration.yaml` or equivalent runtime config.
  - `host`: bind host for local validation.
  - `port`: bind port for local validation.
  - `default_actor`: fallback actor for service-level defaults where already supported.
- Validation:
  - `db_url` must be present and use the supported runtime database scheme.
  - `mcp_config_path` must resolve to a readable configuration file.
  - `port` must be an integer from 1 to 65535.

### 2. WebTierConfig

- Purpose: Runtime configuration for the Flask presentation tier.
- Fields:
  - `session_secret`: Flask session signing secret.
  - `mcp_rpc_url`: full HTTP URL to the MCP wrapper `POST /rpc` endpoint.
  - `host`: bind host for local validation.
  - `port`: bind port for local validation.
  - `timeout_seconds`: timeout for synchronous HTTP requests to the MCP wrapper.
- Validation:
  - `session_secret` must be non-empty.
  - `mcp_rpc_url` must be an absolute HTTP/HTTPS URL.
  - `timeout_seconds` must be greater than 0.

### 3. JsonRpcRequest

- Purpose: Canonical request envelope sent from the Flask web tier to the MCP wrapper.
- Fields:
  - `jsonrpc`: must equal `"2.0"`.
  - `id`: string or integer request identifier.
  - `method`: MCP method name such as `workflow.list` or `user_logon`.
  - `params`: object payload for the selected method.
- Validation:
  - `method` must be a string.
  - `params` must be an object.
  - malformed JSON or malformed envelope is treated as a transport-level failure.

### 4. JsonRpcResponse

- Purpose: Canonical response envelope returned by the MCP wrapper.
- Fields:
  - `jsonrpc`: `"2.0"`.
  - `id`: echoes the request id when available.
  - `result`: object payload for successful MCP execution.
  - `error`: object payload with `code`, `message`, and optional `data` for JSON-RPC application errors.
- Validation:
  - exactly one of `result` or `error` must be present for a valid JSON-RPC application response.
  - valid JSON-RPC application errors are returned with HTTP 200.
  - malformed HTTP/JSON or server failures may return HTTP 400/500.

### 5. WebSessionState

- Purpose: User session state held in the Flask web tier.
- Fields:
  - `user_id`: authenticated username.
  - `active_workflow_name`: selected workflow context.
  - `csrf_token`: CSRF token for form submissions.
- Validation:
  - `active_workflow_name` may only be present for authenticated sessions.
  - `csrf_token` must be verified on state-changing form posts.

### 6. MigratedProductionSurface

- Purpose: Scope boundary for production-equivalent route/template parity.
- Fields:
  - `health_routes`
  - `auth_routes`
  - `workspace_routes`
  - `workflow_crud_routes`
  - `role_crud_routes`
  - `interaction_crud_routes`
  - `guard_crud_routes`
  - `interaction_component_crud_routes`
- Validation:
  - debug-only or experimental Quart surfaces are excluded from parity requirements.

## Relationships

- `WebTierConfig.mcp_rpc_url` targets the MCP wrapper's `JsonRpcRequest` interface.
- `JsonRpcRequest.method` resolves through the in-process MCP dispatcher to existing handler/service logic.
- `JsonRpcResponse.result` drives Flask route outcomes and template rendering.
- `WebSessionState.active_workflow_name` constrains which entity-management routes are available in the migrated UI.

## State Transitions

### Authentication Session

1. Anonymous user requests `GET /login`.
2. Successful `user_logon` JSON-RPC response populates `user_id` and clears stale workflow context.
3. User selects a workflow, populating `active_workflow_name`.
4. `user_logoff` or session clear removes all web-tier session state.

### JSON-RPC Transport

1. Flask route builds `JsonRpcRequest`.
2. Synchronous MCP client posts request to wrapper.
3. Wrapper validates envelope.
4. Wrapper dispatches to existing MCP handler/service logic.
5. Wrapper returns `JsonRpcResponse` under HTTP 200 for valid JSON-RPC execution, or HTTP 400/500 for malformed transport cases.