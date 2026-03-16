# Contract: MCP Session Lifecycle

**Feature**: `006-web-tier-integration`  
**Transport**: SSE (Server-Sent Events) via official `mcp` Python SDK  
**Endpoint**: `MCP_SERVER_URL` (env var, default `http://127.0.0.1:5001/sse`)

---

## Connection Pattern

```python
# quart_web/src/clients/mcp_client.py
from contextlib import AsyncExitStack
from mcp.client.sse import sse_client
from mcp import ClientSession

class MCPClientWrapper:
    def __init__(self, url: str, timeout: float = 10.0):
        self._url = url
        self._timeout = timeout
        self._session: ClientSession | None = None
        self._stack: AsyncExitStack | None = None

    async def connect(self) -> None:
        """Open SSE stream and initialize MCP ClientSession."""
        self._stack = AsyncExitStack()
        read, write = await self._stack.enter_async_context(sse_client(self._url))
        self._session = await self._stack.enter_async_context(ClientSession(read, write))
        await self._session.initialize()

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Call a tool with 10s timeout. Connects lazily if not connected."""
        if self._session is None:
            await self.connect()
        result = await asyncio.wait_for(
            self._session.call_tool(tool_name, arguments=arguments),
            timeout=self._timeout
        )
        # result.content[0].text is JSON string; parse it
        import json
        return json.loads(result.content[0].text)

    async def close(self) -> None:
        """Close SSE stream and exit all context managers."""
        if self._stack:
            await self._stack.aclose()
            self._stack = None
            self._session = None
```

---

## Singleton Lifetime

| Event | Action |
|-------|--------|
| `create_app()` called | `MCPClientWrapper(url=MCP_SERVER_URL)` created, stored on `app.mcp_client` |
| First `call_tool()` request | `connect()` called lazily; SSE stream opened |
| `@app.after_serving` | `await app.mcp_client.close()` called; stream closed cleanly |
| Process signal / SIGTERM | Quart calls `after_serving` hooks; stream closed |

---

## State Machine

```
[unconnected]
  ↓ first call_tool() → connect()
[connected]
  ↓ timeout expires → TimeoutError
[timeout_error]     ← route renders error page; session stays connected
  ↓ next call succeeds → back to [connected]
  ↓ SSE stream drops
[connection_error]  ← MCPConnectionError raised; landing page shows "MCP unavailable"
  ↓ app restart or reconnect
[connected]
```

---

## Tool Call Wire Format

The `mcp` SDK handles serialization. For reference, each call uses JSON-RPC 2.0:

**Request** (SDK-generated):
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 1,
  "params": {
    "name": "workflow.list",
    "arguments": {"limit": 20}
  }
}
```

**Response** (from FastMCP server):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {"type": "text", "text": "{\"status\": \"success\", \"records\": [...]}"}
    ]
  }
}
```

> The web tier calls `json.loads(result.content[0].text)` to get the response dict.

---

## Timeout Policy

- All tool calls wrapped in `asyncio.wait_for(..., timeout=10.0)`
- Timeout value configurable via `MCP_TIMEOUT` env var (default 10 seconds)
- `TimeoutError` propagates from `call_tool()` → route handler wraps in HTTP 504 error page
- NFR-003: 90th-percentile response time budget is 2s; the 10s timeout is a hard ceiling

---

## Reconnection Policy

- Current implementation: **no automatic reconnect** — any connection drop becomes a `MCPConnectionError`
- Landing page (`GET /`) performs a health check; if MCP is down, form inputs are disabled
- Future enhancement: exponential backoff reconnect loop (out of scope for this feature)

---

## Error Types Raised by MCPClientWrapper

| Exception | When | HTTP response |
|-----------|------|---------------|
| `MCPTimeoutError(TimeoutError)` | `asyncio.wait_for` deadline exceeded | 504 error page |
| `MCPConnectionError(Exception)` | SSE stream failed to open or `initialize()` failed | 503 error page |

---

## Environment Variables

| Variable | Default | Required |
|----------|---------|----------|
| `MCP_SERVER_URL` | `http://127.0.0.1:5001/sse` | Yes |
| `SESSION_SECRET` | — | Yes (no default in prod) |
| `MCP_TIMEOUT` | `10` | No |
