# Quickstart: Full Stack WSGI Migration

## Goal

Validate the canonical PythonAnywhere-compatible stack locally using two separate Flask WSGI applications communicating over HTTP.

## 1. Install dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

## 2. Configure environment

Create or update `.env` with values equivalent to:

```env
DB_URL=mysql+pymysql://user:password@127.0.0.1:3306/pdfa_workflow?charset=utf8mb4
DEFAULT_ACTOR=local_dev
MCP_CONFIG_PATH=WB-Workflow-Configuration.yaml

MCP_WRAPPER_HOST=127.0.0.1
MCP_WRAPPER_PORT=5001

FLASK_HOST=127.0.0.1
FLASK_PORT=5000
SESSION_SECRET=replace-with-a-random-secret-value
MCP_RPC_URL=http://127.0.0.1:5001/rpc
```

## 3. Start the MCP Flask wrapper

```powershell
python -m mcp_server.src.wsgi_app
```

Expected result:

- a synchronous Flask WSGI app listens on `http://127.0.0.1:5001`
- `POST /rpc` accepts JSON-RPC requests
- no SSE or ASGI runtime is required

## 4. Start the Flask web tier

```powershell
python -m flask_web.src.app
```

Expected result:

- the web tier listens on `http://127.0.0.1:5000`
- health and login flows communicate with the MCP wrapper through `MCP_RPC_URL`

## 5. Smoke-test the MCP wrapper

```powershell
$body = @{
  jsonrpc = "2.0"
  id = 1
  method = "get_system_health"
  params = @{}
} | ConvertTo-Json -Depth 5

Invoke-RestMethod `
  -Uri "http://127.0.0.1:5001/rpc" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

## 6. Smoke-test the web tier

- open `http://127.0.0.1:5000/`
- verify health page renders
- verify login, dashboard/workspace, and entity pages follow the migrated Flask path

## 7. Run validation tests

```powershell
pytest mcp_server/tests/ -v --tb=short
pytest flask_web/tests/ -v --tb=short
```

## 8. Deployment intent

- deploy `flask_web` as one WSGI app
- deploy `mcp_server/src/wsgi_app.py` as a separate WSGI app
- keep HTTP JSON-RPC as the only supported inter-app transport