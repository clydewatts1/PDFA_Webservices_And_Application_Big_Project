# Contract: Workflow MCP Tools

**Feature**: `006-web-tier-integration`  
**Source**: `mcp_server/src/lib/tool_catalog.py` (inline definitions, not generated)  
**Transport**: SSE at `MCP_SERVER_URL` (default `http://127.0.0.1:5001/sse`)

> **Note**: Workflow is the only entity whose business key is a single field (`WorkflowName`).  
> It does NOT get a `WorkflowName` filter on `workflow.list` — the list always returns all active workflows.  
> All mutating calls require an `actor` parameter (the authenticated username from session).

---

## workflow.list

**Description**: List all active workflows with optional pagination.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Maximum records to return |
| `offset` | integer | No | Number of records to skip |

**Example call** (from `MCPClientWrapper.call_tool`):

```python
await mcp_client.call_tool("workflow.list", {})
await mcp_client.call_tool("workflow.list", {"limit": 20, "offset": 0})
```

**Success response**:
```json
{
  "status": "success",
  "records": [
    {
      "WorkflowName": "example_workflow",
      "WorkflowDescription": "Human-readable description",
      "WorkflowContextDescription": "AI context",
      "WorkflowStateInd": "active",
      "EffFromDateTime": "2024-01-01T00:00:00",
      "EffToDateTime": "9999-12-31T00:00:00",
      "DeleteInd": 0,
      "InsertUserName": "admin",
      "UpdateUserName": "admin"
    }
  ]
}
```

---

## workflow.get

**Description**: Get the active workflow record by WorkflowName.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `WorkflowName` | string | Yes | Unique name of the workflow |

**Example call**:
```python
await mcp_client.call_tool("workflow.get", {"WorkflowName": "my_workflow"})
```

**Error response** (not found):
```json
{"status": "error", "code": "entity_not_found", "message": "workflow 'my_workflow' not found or not active."}
```

---

## workflow.create

**Description**: Create a new workflow.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `WorkflowName` | string | Yes | Unique name for the workflow |
| `WorkflowDescription` | string | No | Human-readable description |
| `WorkflowContextDescription` | string | No | AI-friendly context |
| `WorkflowStateInd` | string | No | Workflow state indicator |
| `actor` | string | Yes | Username performing the action (from `session["user_id"]`) |

**Example call**:
```python
await mcp_client.call_tool("workflow.create", {
    "WorkflowName": "my_workflow",
    "WorkflowDescription": "My workflow description",
    "actor": session["user_id"]
})
```

---

## workflow.update

**Description**: Update an existing workflow; creates a new SCD Type-2 version.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `WorkflowName` | string | Yes | Unique name of the workflow to update |
| `WorkflowDescription` | string | No | Updated description |
| `WorkflowContextDescription` | string | No | Updated AI context |
| `WorkflowStateInd` | string | No | Updated state indicator |
| `actor` | string | Yes | Username performing the update |

---

## workflow.delete

**Description**: Soft-delete the active workflow (sets `DeleteInd=1`).

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `WorkflowName` | string | Yes | Unique name of the workflow to delete |
| `actor` | string | Yes | Username performing the delete |

**Example call**:
```python
await mcp_client.call_tool("workflow.delete", {
    "WorkflowName": "my_workflow",
    "actor": session["user_id"]
})
```

---

## Error Codes

| Code | Description |
|------|-------------|
| `entity_not_found` | WorkflowName does not exist or is already deleted |
| `invalid_input` | Required parameter missing or type mismatch |
| `database_error` | Underlying DB failure |
