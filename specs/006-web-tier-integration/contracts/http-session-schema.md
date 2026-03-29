# Contract: HTTP Session Schema

**Feature**: `006-web-tier-integration`  
**Storage**: Quart signed cookie session (dev); optionally Redis-backed via `quart-session` (prod)  
**Library**: Built-in Quart `session` (backed by `itsdangerous`), `SECRET_KEY` from env

---

## Session Dictionary Schema

```python
# Fields present after successful login
session: dict = {
    "user_id": str,                    # Required post-login.
                                       # Set from user_logon response field "username".
                                       # Cleared on logout or session expiry.
    "active_workflow_name": str | None # Set after workspace selection step.
                                       # Initially absent (KeyError / None).
                                       # Never None once past /dashboard.
}
```

---

## Lifecycle Transitions

```
[Pre-login]
  session = {}   (no fields set)
  → Any route except GET / and GET /login → 302 redirect to /login

[POST /login - SUCCESS]
  response = await mcp_client.call_tool("user_logon", {"username": ..., "password": ...})
  session["user_id"] = response["username"]     # or response["user_id"] per auth_service
  → Redirect to GET /dashboard

[POST /login - DENIED]
  session unchanged
  → Re-render login.html with error banner

[POST /dashboard - workflow selected]
  session["active_workflow_name"] = form.workflow_name.data
  → Redirect to GET /entities

[POST /logout]
  await mcp_client.call_tool("user_logoff", {"username": session["user_id"]})
  session.clear()
  → Redirect to GET /

[Session expired / tampered]
  Quart verifies HMAC signature on every request
  If invalid → session = {}  → 302 redirect to /login
```

---

## Cookie Settings

| Attribute | Value | Notes |
|-----------|-------|-------|
| Name | `session` | Quart default |
| Signing | HMAC via `itsdangerous` | Uses `SECRET_KEY` env var |
| `HttpOnly` | True | Prevents JS access |
| `SameSite` | `Strict` | Set on `SESSION_COOKIE_SAMESITE` |
| `Secure` | True in prod | Set on `SESSION_COOKIE_SECURE` |
| TTL / Expiry | Browser session (default) | Extend via `PERMANENT_SESSION_LIFETIME` |

---

## Route Protection Rules

| Route Pattern | Rule |
|---------------|------|
| `GET /` | Public — no session check |
| `GET /login`, `POST /login` | Public |
| `GET /dashboard`, `POST /dashboard` | Requires `session["user_id"]` |
| `GET /entities` | Requires `session["user_id"]` + `session["active_workflow_name"]` |
| `GET /workflows`, `GET /roles`, `GET /interactions`, `GET /guards`, `GET /interaction-components` | Requires both session fields |
| All entity CRUD routes | Requires both session fields |
| `POST /logout` | Requires `session["user_id"]` |

---

## Authentication Response Shape

```python
# From mcp_server/src/services/auth_service.py (user_logon)
success_response = {
    "status": "SUCCESS",
    "username": "<authenticated username>"
    # Additional fields may be present
}
denied_response = {
    "status": "DENIED",
    # Additional fields may be present
}
```

> **Implementation note**: The session field `user_id` is set from `response["username"]`  
> in the success case. The field name in the response is `"username"`, not `"user_id"`.  
> The session uses `user_id` as the key for clarity at the web tier.

---

## Security Constraints

1. `SECRET_KEY` MUST be set from environment variable; never hardcode.
2. `SECRET_KEY` must be at least 32 bytes of random data (`secrets.token_hex(32)`).
3. `SESSION_COOKIE_SECURE = True` in production config.
4. `SESSION_COOKIE_SAMESITE = "Strict"` prevents CSRF via cross-site requests.
5. `CSRFProtect(app)` from `quart-wtf` adds CSRF token validation for all forms (FR-014).
6. `WTF_CSRF_ENABLED = False` ONLY in test config.
