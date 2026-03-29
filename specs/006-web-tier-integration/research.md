# Phase 0 Research: Simplified Web Tier Integration

**Feature**: `006-web-tier-integration` | **Date**: 2026-03-16  
**Status**: Complete — all NEEDS CLARIFICATION items resolved  

---

## 1. Quart App Architecture

- **Decision**: Quart `create_app()` factory function with Blueprint registration, in-memory signed cookie sessions for development, `quart-session` Redis backend for production.
- **Rationale**: Mirrors the existing `flask_web/src/app.py` factory pattern (`create_app() -> Flask`). Quart is a near-drop-in async replacement for Flask; factory functions support per-request scoping and testability. The existing Flask factory registers three blueprints (`workflow_bp`, `dependent_bp`, `instance_bp`) — the Quart factory will register four (`health_bp`, `auth_bp`, `workspace_bp`, `entity_bp`).
- **Alternatives considered**: `@app.before_serving` async startup hook — rejected by spec Clarification Q5; would block startup if MCP unreachable.
- **References**: [Quart docs: Application structure](https://quart.palletsprojects.com/en/latest/how_to_guides/application_structure.html), existing `flask_web/src/app.py`

**Key patterns**:
```python
# quart_web/src/app.py
from quart import Quart
from quart_wtf import CSRFProtect
from .clients.mcp_client import MCPClientWrapper

csrf = CSRFProtect()
mcp_client: MCPClientWrapper | None = None

def create_app() -> Quart:
    app = Quart(__name__)
    app.secret_key = os.environ["SESSION_SECRET"]
    app.config["WTF_CSRF_ENABLED"] = True
    app.config["MCP_SERVER_URL"] = os.environ.get("MCP_SERVER_URL", "http://127.0.0.1:5001/sse")
    csrf.init_app(app)
    global mcp_client
    mcp_client = MCPClientWrapper(url=app.config["MCP_SERVER_URL"])
    # Register blueprints
    from .routes.health import health_bp
    from .routes.auth import auth_bp
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    return app
```

---

## 2. MCP Python SDK Integration (SSE Transport)

- **Decision**: Use `mcp.client.sse.sse_client` context manager with `mcp.ClientSession` wrapper. Wrap in an `asyncio.TaskGroup`-managed background task to hold the SSE connection open for the application lifetime. Expose a `call_tool(name, **kwargs)` helper that wraps `session.call_tool()` with a 10-second `asyncio.wait_for()` timeout.
- **Rationale**: The existing `flask_web/src/clients/mcp_client.py` uses synchronous `requests.post` to a JSON-RPC endpoint — **this is not the official MCP SDK and must be replaced**. The official `mcp` package (`pip install mcp`) exposes `sse_client` for long-lived SSE connections. The singleton session avoids repeated SSE handshakes per route request.
- **Alternatives considered**: Per-request SSE connections — rejected; SSE handshake overhead is too high for request-level use. Streamable-HTTP transport — rejected by spec Clarification Q1; SSE chosen for alignment with existing Feature 005 infrastructure.
- **References**: `mcp` package README, `mcp_server/src/lib/transport_parity.py`, spec Clarification Q1

**Key patterns**:
```python
# quart_web/src/clients/mcp_client.py
import asyncio
from contextlib import AsyncExitStack
from mcp.client.sse import sse_client
from mcp import ClientSession

class MCPClientWrapper:
    def __init__(self, url: str, timeout: float = 10.0) -> None:
        self._url = url
        self._timeout = timeout
        self._session: ClientSession | None = None
        self._stack = AsyncExitStack()

    async def connect(self) -> None:
        """Open SSE connection. Call once from health-check route on first request."""
        read, write = await self._stack.enter_async_context(sse_client(self._url))
        self._session = await self._stack.enter_async_context(ClientSession(read, write))
        await self._session.initialize()

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        if self._session is None:
            await self.connect()
        try:
            result = await asyncio.wait_for(
                self._session.call_tool(tool_name, arguments=arguments),
                timeout=self._timeout,
            )
        except asyncio.TimeoutError:
            raise MCPTimeoutError(tool_name)
        return result.content

    async def close(self) -> None:
        await self._stack.aclose()
```

**Tool name registry** (from `mcp_server/src/lib/tool_catalog.py`):

| Tool | Parameters | Returns |
|------|-----------|---------|
| `get_system_health` | none | `{status, database_status, ...}` |
| `user_logon` | `username`, `password` | `{status: "SUCCESS"\|"DENIED", username, ...}` |
| `user_logoff` | `username` | `{status, ...}` |
| `workflow.list` | `limit?`, `offset?` | `[{WorkflowName, WorkflowDescription, ...}]` |
| `workflow.get` | `WorkflowName` | `{WorkflowName, ...}` |
| `workflow.create` | `WorkflowName`, optional fields, `actor` | `{...}` |
| `workflow.update` | `WorkflowName`, optional fields, `actor` | `{...}` |
| `workflow.delete` | `WorkflowName`, `actor` | `{...}` |
| `role.list` | `WorkflowName?`, `limit?`, `offset?` | `[{RoleName, WorkflowName, ...}]` |
| `role.get` | `RoleName`, `WorkflowName` | `{RoleName, WorkflowName, ...}` |
| `role.create` | `RoleName`, `WorkflowName`, optional fields, `actor` | `{...}` |
| `role.update` | `RoleName`, `WorkflowName`, optional fields, `actor` | `{...}` |
| `role.delete` | `RoleName`, `WorkflowName`, `actor` | `{...}` |
| `interaction.list` | `WorkflowName?`, `limit?`, `offset?` | `[...]` |
| `interaction.get` | `InteractionName`, `WorkflowName` | `{...}` |
| `guard.list` | `WorkflowName?`, `limit?`, `offset?` | `[...]` |
| `guard.get` | `GuardName`, `WorkflowName` | `{...}` |
| `interaction_component.list` | `WorkflowName?`, `limit?`, `offset?` | `[...]` |
| `interaction_component.get` | `InteractionComponentName`, `WorkflowName` | `{...}` |

---

## 3. HTTP Session Schema

- **Decision**: Quart's built-in signed cookie session (default). Store `user_id`, `active_workflow_name`, `username` in session dict. No server-side session store for Phase 1 (dev). For production, `quart-session` with Redis backend configurable via `SESSION_TYPE=redis` env var.
- **Rationale**: Quart's built-in session is identical to Flask's — signed JSON cookies via `itsdangerous`. It requires only `app.secret_key` (from `SESSION_SECRET` env var). Adding Redis is a one-line change (`quart-session`) and doesn't require database changes. The spec assumption is single-user MVP; concurrent multi-user sessions are out of scope.
- **Alternatives considered**: JWT tokens in `Authorization` header — rejected; requires JavaScript for storage. Database-backed sessions — rejected; no direct DB access in web tier.
- **References**: Quart session docs, `quart-session` README, spec NFR-005, spec Clarifications Q3

**HTTP Session fields**:
```python
# What to store in session after successful login
session["user_id"] = username           # str: from user_logon response
session["active_workflow_name"] = None  # str | None: set at workspace selection
```

**Cookie security settings**:
```python
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Strict"
app.config["SESSION_COOKIE_SECURE"] = True   # prod only; False in dev
```

---

## 4. Form Handling Patterns (Bootstrap 5 + quart-wtf)

- **Decision**: `quart-wtf` for CSRF token generation and validation on all POST forms. Server-side WTForms field validation as secondary layer; HTML5 `required` attributes for client-side UX hints only (not trusted). On validation error: re-render the same page, preserve user input via WTForms `form.data`, render error messages in Bootstrap `alert-danger` blocks.
- **Rationale**: Spec Clarification Q1 (CSRF via `quart-wtf`), Q3 (same-page re-render on error), Q4 (show business fields only). `quart-wtf` wraps `flask-wtf` for async Quart; CSRF integration is transparent once `CSRFProtect(app)` is called in the factory. Business-only field mapping is enforced at the form class level (no `EffFromDateTime` etc. in form fields).
- **Alternatives considered**: Custom manual CSRF tokens — rejected in favour of `quart-wtf` per Q1. Client-side JavaScript form pre-validation — rejected; spec FR-001 prohibits JS state management beyond `onclick` submit guard.
- **References**: Bootstrap 5 Forms documentation, `quart-wtf` README, spec FR-005, FR-011, Clarifications Q1/Q3/Q4

**Form template pattern**:
```html
<!-- base form template snippet -->
<form method="POST" action="{{ action_url }}">
  {{ form.csrf_token }}
  <div class="mb-3">
    <label for="{{ form.role_name.id }}" class="form-label">Role Name</label>
    {{ form.role_name(class="form-control") }}
    {% if form.role_name.errors %}
      <div class="alert alert-danger">{{ form.role_name.errors|join(', ') }}</div>
    {% endif %}
  </div>
  <button type="submit" class="btn btn-primary"
          onclick="this.disabled=true; this.form.submit()">Save</button>
</form>
```

**Entity form field visibility** (business only, per Clarification Q4):

| Entity | Visible fields | Hidden (MCP-managed) |
|--------|---------------|---------------------|
| Workflow | `WorkflowName`, `WorkflowDescription`, `WorkflowContextDescription`, `WorkflowStateInd` | `EffFromDateTime`, `EffToDateTime`, `DeleteInd`, `InsertUserName`, `UpdateUserName` |
| Role | `RoleName`, `WorkflowName`, `RoleDescription`, `RoleContextDescription`, `RoleConfiguration`, `RoleConfigurationDescription`, `RoleConfigurationContextDescription` | Same temporal/audit set |
| Interaction | `InteractionName`, `WorkflowName`, `InteractionDescription`, `InteractionContextDescription`, `InteractionType` | Same temporal/audit set |
| Guard | `GuardName`, `WorkflowName`, `GuardDescription`, `GuardContextDescription`, `GuardType`, `GuardConfiguration` | Same temporal/audit set |
| InteractionComponent | `InteractionComponentName`, `WorkflowName`, `InteractionComponentRelationShip`, `InteractionComponentDescription`, `InteractionComponentContextDescription`, `SourceName`, `TargetName` | Same temporal/audit set |

---

## 5. Testing Architecture

- **Decision**: pytest-asyncio with `asyncio_mode = "auto"` in `pytest.ini`. Quart test client via `app.test_client()` (async context manager). MCP session mocked with `unittest.mock.AsyncMock`. Separate `conftest.py` for web tier (`quart_web/tests/`) vs MCP tier (`mcp_server/tests/`) — no shared fixtures across tiers.
- **Rationale**: Spec FR-004 (route tests use AsyncMock), Constitution Principle VI (boundary-aware testing), NFR from spec. Quart's `test_client()` is natively async; pytest-asyncio `asyncio_mode = "auto"` removes need for `@pytest.mark.asyncio` on every test. The existing MCP tier tests already use real database fixtures — those remain unchanged.
- **Alternatives considered**: `aioresponses` to mock HTTP at the aiohttp level — rejected; too low-level and couples tests to transport implementation. Using a real running MCP server in unit tests — rejected; violates tier isolation and slows suite.
- **References**: pytest-asyncio docs, Quart testing guide, spec FR-004, Constitution Principle VI

**Test fixture pattern**:
```python
# quart_web/tests/conftest.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from quart_web.src.app import create_app

@pytest.fixture
def mock_mcp():
    mock = AsyncMock()
    mock.call_tool = AsyncMock(return_value={"status": "SUCCESS"})
    return mock

@pytest.fixture
async def client(mock_mcp):
    app = create_app()
    app.config["WTF_CSRF_ENABLED"] = False  # disable CSRF in tests only
    app.config["TESTING"] = True
    # Inject mock into app
    import quart_web.src.app as app_module
    app_module.mcp_client = mock_mcp
    async with app.test_client() as client:
        yield client
```

**Test coverage targets**:

| Test file | Routes covered | Mock target |
|-----------|---------------|-------------|
| `test_health.py` | `GET /` | `mcp_client.call_tool("get_system_health")` |
| `test_auth.py` | `GET /login`, `POST /login`, `POST /logout` | `call_tool("user_logon")`, `call_tool("user_logoff")` |
| `test_workspace.py` | `GET /dashboard`, `POST /dashboard` | `call_tool("workflow.list")` |
| `test_entity_routes.py` | `GET /roles`, `GET /roles/new`, `POST /roles/new`, `GET /roles/<name>/edit`, `POST /roles/<name>/edit`, `POST /roles/<name>/delete` | `call_tool("role.list")`, `call_tool("role.get")`, etc. |

---

## Summary of All Decisions

| Area | Decision |
|------|----------|
| Web framework | Quart (async Flask-compatible), `create_app()` factory |
| MCP SDK | Official `mcp` package, `sse_client` + `ClientSession` singleton via `AsyncExitStack` |
| MCP transport | SSE at `MCP_SERVER_URL` (default `http://127.0.0.1:5001/sse`) |
| MCP timeout | `asyncio.wait_for(timeout=10)` on every tool call |
| Session backend | Quart signed cookie (dev), `quart-session` + Redis (prod) |
| CSRF | `quart-wtf` `CSRFProtect`, `WTF_CSRF_ENABLED=False` in test config |
| Form validation | Server-side via WTForms; same-page re-render on error |
| Field visibility | Business attributes only; temporal/audit hidden |
| Double-submit guard | `onclick="this.disabled=true; this.form.submit()"` on submit buttons |
| Testing | pytest-asyncio auto mode, Quart `test_client()`, `AsyncMock` for MCP |
| Template root | `quart_web/src/templates/` (not `flask_web/`) |
| Env var | `MCP_SERVER_URL`, `SESSION_SECRET` |
