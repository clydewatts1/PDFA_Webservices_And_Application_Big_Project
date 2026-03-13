# MCP JSON-RPC Contract (Increment 1)

## Transport
- Protocol: HTTP + JSON-RPC 2.0
- Required in this increment: JSON-RPC
- Deferred: SSE streaming endpoints

## Common Envelope
### Request
```json
{
  "jsonrpc": "2.0",
  "id": "<uuid-or-int>",
  "method": "<domain.operation>",
  "params": { }
}
```

### Success Response
```json
{
  "jsonrpc": "2.0",
  "id": "<same-id>",
  "result": { }
}
```

### Error Response
```json
{
  "jsonrpc": "2.0",
  "id": "<same-id-or-null>",
  "error": {
    "code": 4000,
    "message": "ValidationError",
    "data": {
      "field": "WorkflowName",
      "reason": "duplicate_active_key"
    }
  }
}
```

## Methods

### Workflow
- `workflow.create`
- `workflow.update`
- `workflow.get`
- `workflow.list`
- `workflow.delete`

### Dependent Entities
- `role.create|update|get|list|delete`
- `interaction.create|update|get|list|delete`
- `guard.create|update|get|list|delete`
- `interaction_component.create|update|get|list|delete`
- `unit_of_work.create|update|get|list|delete`

### Instance
- `instance.create`
- `instance.update_state`
- `instance.get`
- `instance.list`

## Required Behavioral Guarantees
- Updates preserve exactly one active current row per business key.
- Prior active rows are closed (`EffToDateTime`) and moved to history semantics.
- Instance creation replicates baseline dependent definitions as instance-scoped rows in fixed tables.
- Runtime creation of per-instance physical tables is forbidden.

## Validation Errors (minimum set)
- `duplicate_active_key`
- `invalid_workflow_reference`
- `invalid_temporal_window`
- `invalid_delete_indicator`
- `invalid_instance_state`
