# Contract: MCP Flask WSGI JSON-RPC Endpoint

## Purpose

Define the canonical HTTP interface exposed by `mcp_server/src/wsgi_app.py` for PythonAnywhere-compatible deployment.

## Endpoint

- Method: `POST`
- Path: `/rpc`
- Content-Type: `application/json`

## Request Envelope

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "get_system_health",
  "params": {}
}
```

## Request Rules

- `jsonrpc` must equal `"2.0"`.
- `id` may be string or integer.
- `method` must be a string.
- `params` must be a JSON object.

## Success Response

HTTP status: `200`

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "status": "SUCCESS",
    "health_status": "CONNECTED"
  }
}
```

## JSON-RPC Application Error Response

HTTP status: `200`

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32601,
    "message": "Method not found",
    "data": {
      "method": "unknown.method"
    }
  }
}
```

## Transport-Level Error Behavior

- HTTP `400`: malformed JSON, invalid content type, or non-JSON request body that cannot be interpreted as a JSON-RPC request.
- HTTP `500`: unexpected wrapper failure before a valid JSON-RPC response can be constructed.

## In-Scope MCP Methods for Production Web Flow

- `get_system_health`
- `user_logon`
- `user_logoff`
- `workflow.list`, `workflow.get`, `workflow.create`, `workflow.update`, `workflow.delete`
- `role.list`, `role.get`, `role.create`, `role.update`, `role.delete`
- `interaction.list`, `interaction.get`, `interaction.create`, `interaction.update`, `interaction.delete`
- `guard.list`, `guard.get`, `guard.create`, `guard.update`, `guard.delete`
- `interaction_component.list`, `interaction_component.get`, `interaction_component.create`, `interaction_component.update`, `interaction_component.delete`

## Dispatch Rule

- The wrapper dispatches requests through the existing MCP handler/tool adapter and service layer.
- The wrapper must not implement business logic independently of the existing MCP services.