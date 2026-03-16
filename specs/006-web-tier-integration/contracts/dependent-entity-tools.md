# Contract: Role, Interaction, Guard, InteractionComponent MCP Tools

**Feature**: `006-web-tier-integration`  
**Source**: `mcp_server/src/lib/tool_catalog.py` (`_crud_tool_definitions`) + `mcp_server/src/services/dependent_service.py`  
**Transport**: SSE at `MCP_SERVER_URL`

> **Pattern**: All four entities share the same CRUD contract shape. Business keys are always  
> `[EntityName, WorkflowName]`. The `WorkflowName` on `{entity}.list` is an **optional filter**  
> (driven by `requires_workflow_fk=True`). `InstanceName` is excluded from all web forms  
> (internal use only).

---

## ROLE tools

**Business keys**: `["RoleName", "WorkflowName"]`  
**Optional form fields** (visible in web form):
`RoleDescription`, `RoleContextDescription`, `RoleConfiguration`,  
`RoleConfigurationDescription`, `RoleConfigurationContextDescription`

### role.list

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `WorkflowName` | string | No | Filter by workflow; pass `session["active_workflow_name"]` |
| `limit` | integer | No | Max records |
| `offset` | integer | No | Skip N records |

```python
await mcp_client.call_tool("role.list", {"WorkflowName": session["active_workflow_name"]})
```

**Response**: `{"status": "success", "records": [{...}, ...]}`

### role.get

| Parameter | Type | Required |
|-----------|------|----------|
| `RoleName` | string | Yes |
| `WorkflowName` | string | Yes |

```python
await mcp_client.call_tool("role.get", {"RoleName": name, "WorkflowName": session["active_workflow_name"]})
```

### role.create

| Parameter | Type | Required |
|-----------|------|----------|
| `RoleName` | string | Yes |
| `WorkflowName` | string | Yes |
| `RoleDescription` | string | No |
| `RoleContextDescription` | string | No |
| `RoleConfiguration` | string | No |
| `RoleConfigurationDescription` | string | No |
| `RoleConfigurationContextDescription` | string | No |
| `actor` | string | Yes |

### role.update

Same parameters as `role.create`. Business keys identify the record; optional fields are patched.

### role.delete

| Parameter | Type | Required |
|-----------|------|----------|
| `RoleName` | string | Yes |
| `WorkflowName` | string | Yes |
| `actor` | string | Yes |

---

## INTERACTION tools

**Business keys**: `["InteractionName", "WorkflowName"]`  
**Optional form fields**: `InteractionDescription`, `InteractionContextDescription`, `InteractionType`

### interaction.list

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `WorkflowName` | string | No | Pass `session["active_workflow_name"]` |
| `limit` | integer | No | |
| `offset` | integer | No | |

### interaction.get

| Parameter | Type | Required |
|-----------|------|----------|
| `InteractionName` | string | Yes |
| `WorkflowName` | string | Yes |

### interaction.create / interaction.update

| Parameter | Type | Required |
|-----------|------|----------|
| `InteractionName` | string | Yes |
| `WorkflowName` | string | Yes |
| `InteractionDescription` | string | No |
| `InteractionContextDescription` | string | No |
| `InteractionType` | string | No |
| `actor` | string | Yes |

### interaction.delete

| Parameter | Type | Required |
|-----------|------|----------|
| `InteractionName` | string | Yes |
| `WorkflowName` | string | Yes |
| `actor` | string | Yes |

---

## GUARD tools

**Business keys**: `["GuardName", "WorkflowName"]`  
**Optional form fields**: `GuardDescription`, `GuardContextDescription`, `GuardType`, `GuardConfiguration`

### guard.list / guard.get

Same pattern. `guard.list` has optional `WorkflowName` filter.

### guard.create / guard.update

| Parameter | Type | Required |
|-----------|------|----------|
| `GuardName` | string | Yes |
| `WorkflowName` | string | Yes |
| `GuardDescription` | string | No |
| `GuardContextDescription` | string | No |
| `GuardType` | string | No |
| `GuardConfiguration` | string | No |
| `actor` | string | Yes |

### guard.delete

Business keys + `actor`.

---

## INTERACTION_COMPONENT tools

**Business keys**: `["InteractionComponentName", "WorkflowName"]`  
**Optional form fields**:  
`InteractionComponentRelationShip`, `InteractionComponentDescription`,  
`InteractionComponentContextDescription`, `SourceName`, `TargetName`

### interaction_component.list / interaction_component.get

Same pattern. `interaction_component.list` has optional `WorkflowName` filter.

### interaction_component.create / interaction_component.update

| Parameter | Type | Required |
|-----------|------|----------|
| `InteractionComponentName` | string | Yes |
| `WorkflowName` | string | Yes |
| `InteractionComponentRelationShip` | string | No |
| `InteractionComponentDescription` | string | No |
| `InteractionComponentContextDescription` | string | No |
| `SourceName` | string | No |
| `TargetName` | string | No |
| `actor` | string | Yes |

### interaction_component.delete

Business keys + `actor`.

---

## Shared Error Codes (all entity tools)

| Code | Description |
|------|-------------|
| `entity_not_found` | Record does not exist or has been soft-deleted |
| `invalid_workflow_reference` | WorkflowName is not a valid active workflow |
| `invalid_input` | Required parameter missing or type mismatch |
| `database_error` | Underlying DB failure |

## WorkflowName propagation rule

> For all entity routes: the `WorkflowName` argument passed to MCP tools is always pulled  
> from `session["active_workflow_name"]`. Route handlers MUST NOT trust user-submitted  
> WorkflowName values for scoping queries — read it from session only.
