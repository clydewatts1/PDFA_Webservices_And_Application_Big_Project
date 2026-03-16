# Data Model: Web Tier Integration

**Feature**: `006-web-tier-integration` | **Date**: 2026-03-16  
**Source**: Phase 0 research.md, spec.md, `mcp_server/src/models/` and `mcp_server/src/services/dependent_service.py`

---

## 1. HTTP Session Object

Storage: Quart signed cookie (dev) / Redis (prod via `quart-session`)  
Set-Cookie: `session=<signed-token>; HttpOnly; SameSite=Strict; Secure`

```python
# Contents stored in session dict after login
{
    "user_id": str,             # Required. Username from user_logon success response.
    "active_workflow_name": str # Optional. WorkflowName selected at /dashboard.
                                # None until workspace selection step is complete.
}
```

**State transitions**:
```
Initial (anonymous)
  → [POST /login, user_logon SUCCESS] → Logged-in (user_id set)
  → [POST /dashboard, workflow selected] → Workspace-active (active_workflow_name set)
  → [POST /logout, user_logoff] → Initial (session cleared)
  → [Session timeout / missing] → Redirect to /login
```

**Validation rules**:
- `user_id` must be a non-empty string
- `active_workflow_name` required before accessing any entity list/CRUD route
- Missing session on protected route → HTTP 302 redirect to `/login`

---

## 2. MCP Session (Global Singleton)

```python
# quart_web/src/clients/mcp_client.py
class MCPClientWrapper:
    _url: str                    # From MCP_SERVER_URL env var
    _timeout: float = 10.0       # asyncio.wait_for timeout in seconds
    _session: ClientSession      # mcp.ClientSession (official SDK)
    _stack: AsyncExitStack       # Holds sse_client + ClientSession context managers
```

**States**:

| State | Description | Recovery |
|-------|-------------|----------|
| `unconnected` | Initial state; `connect()` not yet called | Auto-connect on first `call_tool()` |
| `connected` | SSE stream open; `_session.initialize()` completed | N/A |
| `timeout_error` | `asyncio.wait_for` raised `TimeoutError` | Raise `MCPTimeoutError`; route renders error page |
| `connection_error` | SSE handshake or `initialize()` failed | Raise `MCPConnectionError`; `GET /` shows form disabled |

**Initialization sequence**:
```
create_app()
  → MCPClientWrapper created (url=MCP_SERVER_URL)
  → Client NOT connected (unconnected state)
  → GET / called
    → health_route awaits mcp_client.call_tool("get_system_health")
    → call_tool() detects unconnected → calls connect()
    → sse_client(url) opens SSE stream
    → ClientSession(read, write) initialized
    → State: connected
    → get_system_health returns health dict
    → Landing page renders with status
```

---

## 3. Entity Field Schemas

All entities inherit `ControlColumnsMixin` (`mcp_server/src/models/base.py`).  
The temporal/audit columns are managed exclusively by the MCP tier.  
**Web forms expose business attributes only.**

### 3a. Workflow

| Field | Type | Required | Form Visible | Notes |
|-------|------|----------|-------------|-------|
| `WorkflowName` | string(128) | Yes | Yes | Business key; immutable on edit |
| `WorkflowDescription` | text | No | Yes | Human-readable description |
| `WorkflowContextDescription` | text | No | Yes | AI-friendly context |
| `WorkflowStateInd` | string | No | Yes | State indicator |
| `EffFromDateTime` | datetime | MCP | **No** | SCD Type-2 validity start |
| `EffToDateTime` | datetime | MCP | **No** | SCD Type-2 validity end |
| `DeleteInd` | int | MCP | **No** | 0=active, 1=soft-deleted |
| `InsertUserName` | string | MCP | **No** | Audit: created by |
| `UpdateUserName` | string | MCP | **No** | Audit: last updated by |

**MCP tools**: `workflow.list`, `workflow.get`, `workflow.create`, `workflow.update`, `workflow.delete`  
**Business keys for get/update/delete**: `WorkflowName`

### 3b. Role

| Field | Type | Required | Form Visible | Notes |
|-------|------|----------|-------------|-------|
| `RoleName` | string(128) | Yes | Yes | Business key |
| `WorkflowName` | string(128) | Yes | Yes (read-only on edit) | FK to Workflow; prefilled from session |
| `InstanceName` | string(128) | No | No | Internal use; not in business form |
| `RoleDescription` | text | No | Yes | Human-readable description |
| `RoleContextDescription` | text | No | Yes | AI context |
| `RoleConfiguration` | text | No | Yes | Config payload (JSON string) |
| `RoleConfigurationDescription` | text | No | Yes | |
| `RoleConfigurationContextDescription` | text | No | Yes | |
| `EffFromDateTime` | datetime | MCP | **No** | |
| `EffToDateTime` | datetime | MCP | **No** | |
| `DeleteInd` | int | MCP | **No** | |
| `InsertUserName` | string | MCP | **No** | |
| `UpdateUserName` | string | MCP | **No** | |

**MCP tools**: `role.list(WorkflowName?, limit?, offset?)`, `role.get(RoleName, WorkflowName)`, `role.create(...)`, `role.update(...)`, `role.delete(...)`

### 3c. Interaction

| Field | Type | Required | Form Visible | Notes |
|-------|------|----------|-------------|-------|
| `InteractionName` | string(128) | Yes | Yes | Business key |
| `WorkflowName` | string(128) | Yes | Yes (read-only on edit) | Prefilled from session |
| `InstanceName` | string(128) | No | No | |
| `InteractionDescription` | text | No | Yes | |
| `InteractionContextDescription` | text | No | Yes | |
| `InteractionType` | string | No | Yes | |
| *(temporal/audit)* | — | MCP | **No** | |

**MCP tools**: `interaction.list(WorkflowName?, limit?, offset?)`, `interaction.get(InteractionName, WorkflowName)`, `interaction.create(...)`, `interaction.update(...)`, `interaction.delete(...)`

### 3d. Guard

| Field | Type | Required | Form Visible | Notes |
|-------|------|----------|-------------|-------|
| `GuardName` | string(128) | Yes | Yes | Business key |
| `WorkflowName` | string(128) | Yes | Yes (read-only on edit) | |
| `InstanceName` | string(128) | No | No | |
| `GuardDescription` | text | No | Yes | |
| `GuardContextDescription` | text | No | Yes | |
| `GuardType` | string | No | Yes | |
| `GuardConfiguration` | text | No | Yes | |
| *(temporal/audit)* | — | MCP | **No** | |

**MCP tools**: `guard.list(WorkflowName?, limit?, offset?)`, `guard.get(GuardName, WorkflowName)`, `guard.create(...)`, `guard.update(...)`, `guard.delete(...)`

### 3e. InteractionComponent

| Field | Type | Required | Form Visible | Notes |
|-------|------|----------|-------------|-------|
| `InteractionComponentName` | string(128) | Yes | Yes | Business key |
| `WorkflowName` | string(128) | Yes | Yes (read-only on edit) | |
| `InstanceName` | string(128) | No | No | |
| `InteractionComponentRelationShip` | string | No | Yes | |
| `InteractionComponentDescription` | text | No | Yes | |
| `InteractionComponentContextDescription` | text | No | Yes | |
| `SourceName` | string | No | Yes | |
| `TargetName` | string | No | Yes | |
| *(temporal/audit)* | — | MCP | **No** | |

**MCP tools**: `interaction_component.list(WorkflowName?, ...)`, `interaction_component.get(InteractionComponentName, WorkflowName)`, `interaction_component.create(...)`, `interaction_component.update(...)`, `interaction_component.delete(...)`

---

## 4. View Models (per Phase)

### Phase 1: Landing & Auth

```python
@dataclass
class LandingViewModel:
    mcp_healthy: bool           # True if get_system_health returned status=="ok"
    mcp_status_message: str     # Human-readable status string
    login_form: LoginForm       # WTForms LoginForm instance (quart-wtf)

@dataclass
class LoginForm(FlaskForm):
    username: StringField       # required
    password: PasswordField     # required
    # csrf_token injected automatically by CSRFProtect
```

### Phase 2: Workspace Selection

```python
@dataclass
class WorkspaceViewModel:
    workflows: list[dict]       # [{WorkflowName, WorkflowDescription, ...}, ...]
    select_form: WorkspaceSelectForm

@dataclass
class WorkspaceSelectForm(FlaskForm):
    workflow_name: SelectField  # choices populated from workflow.list result
```

### Phase 3: Dashboard

```python
@dataclass
class DashboardViewModel:
    username: str               # from session["user_id"]
    active_workflow_name: str   # from session["active_workflow_name"]
    nav_tabs: list[NavTab]      # [{label, href, entity_type}, ...]

@dataclass
class NavTab:
    label: str                  # e.g., "Roles"
    href: str                   # e.g., "/roles"
    entity_type: str            # e.g., "role"
```

### Phase 4: Entity CRUD

```python
@dataclass
class EntityListViewModel:
    entity_type: str            # e.g., "role"
    active_workflow_name: str
    items: list[dict]           # records from entity.list tool response
    create_url: str             # e.g., "/roles/new"

@dataclass
class EntityEditViewModel:
    entity_type: str
    item: dict                  # current values from entity.get tool response
    form: BaseEntityForm        # WTForms form with current values pre-filled
    action_url: str             # e.g., "/roles/MyRole/edit"
    errors: list[str]           # MCP validation error messages
```

---

## 5. URL Route Map

| Method | Path | Phase | Description |
|--------|------|-------|-------------|
| GET | `/` | 1 | Landing page + health check |
| GET | `/login` | 1 | Login form |
| POST | `/login` | 1 | Submit credentials |
| POST | `/logout` | 1 | Clear session |
| GET | `/dashboard` | 2 | Workflow selection list |
| POST | `/dashboard` | 2 | Select active workflow |
| GET | `/entities` | 3 | Entity navigation dashboard |
| GET | `/workflows` | 4 | Workflow list |
| GET | `/workflows/new` | 4 | Create workflow form |
| POST | `/workflows/new` | 4 | Submit create workflow |
| GET | `/workflows/<name>/edit` | 4 | Edit workflow form |
| POST | `/workflows/<name>/edit` | 4 | Submit update workflow |
| POST | `/workflows/<name>/delete` | 4 | Delete workflow (confirmation POST) |
| GET | `/roles` | 4 | Role list (filtered by active workflow) |
| GET | `/roles/new` | 4 | Create role form |
| POST | `/roles/new` | 4 | Submit create role |
| GET | `/roles/<name>/edit` | 4 | Edit role form |
| POST | `/roles/<name>/edit` | 4 | Submit update role |
| POST | `/roles/<name>/delete` | 4 | Delete role |
| *(same pattern for: `/interactions`, `/guards`, `/interaction-components`)* | | 4 | |
