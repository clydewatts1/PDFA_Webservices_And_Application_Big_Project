# Research: Full Stack WSGI Migration

## Decision 1: Deploy two separate Flask WSGI applications over HTTP

- Decision: Run the Flask web tier and the Flask MCP wrapper as separate WSGI apps that communicate over HTTP.
- Rationale: This preserves the constitution's three-tier boundary in deployment as well as code structure, keeps failure domains separate, and avoids collapsing the web tier and MCP logic into one process.
- Alternatives considered:
  - Single combined Flask process: rejected because it weakens the Database -> MCP Server -> Flask Web Server boundary.
  - Local loopback proxy to an ASGI MCP runtime: rejected because PythonAnywhere does not support the ASGI runtime path that drove this feature.

## Decision 2: Build `mcp_server/src/wsgi_app.py` as a thin adapter over the existing MCP handler map

- Decision: Implement the new wrapper by reusing `build_runtime_tool_adapter(...)` and the existing service-layer-backed handlers rather than duplicating dispatch logic.
- Rationale: The current MCP stack already centralizes business behavior in handler factories and services. Reusing that surface keeps one source of truth for validation, transaction handling, and current/history orchestration.
- Alternatives considered:
  - Reimplement JSON-RPC dispatch in a second business layer: rejected because it introduces logic drift risk.
  - Proxy to a separate MCP network process: rejected because it adds an unnecessary extra hop and operational dependency.

## Decision 3: Keep JSON-RPC errors in HTTP 200 responses for valid requests

- Decision: Return HTTP 200 for valid JSON-RPC requests, including method, validation, and business-level MCP errors. Use HTTP 400/500 only for malformed HTTP/JSON or server-failure conditions.
- Rationale: This matches common JSON-RPC-over-HTTP behavior and keeps the Flask web client simple: transport errors are transport failures, while application errors remain inside the JSON-RPC envelope.
- Alternatives considered:
  - Always return HTTP 200 for every failure mode: rejected because malformed transport input should remain distinguishable.
  - Use broad HTTP status mapping for domain errors: rejected because it would spread business error semantics across two error channels.

## Decision 4: Treat the current Flask JSON-RPC pieces as reusable building blocks, not the final runtime shape

- Decision: Reuse the existing synchronous JSON-RPC patterns already present in `mcp_server/src/api/app.py`, but move the canonical deployment entrypoint to a dedicated `wsgi_app.py` module.
- Rationale: The codebase already contains a synchronous `/rpc` implementation pattern and a synchronous `requests`-based Flask client. The feature should consolidate and elevate those pieces rather than inventing new transport behavior.
- Alternatives considered:
  - Keep `mcp_server/src/api/app.py` as the only runtime entrypoint: rejected because the feature spec explicitly requires a dedicated WSGI wrapper surface.
  - Continue to rely on FastMCP's ASGI network runtime: rejected by the PythonAnywhere hosting constraint.

## Decision 5: Migrate only production Quart flows, not debug or experimental surfaces

- Decision: Port health, authentication, dashboard/workspace navigation, and supported workflow-entity CRUD routes/templates/forms into `flask_web`.
- Rationale: This is the highest-value functional parity set and matches the clarified feature scope.
- Alternatives considered:
  - Migrate every Quart artifact indiscriminately: rejected because it expands scope without improving the production path.
  - Migrate only health/login/dashboard: rejected because it leaves the core entity-management flows incomplete.

## Decision 6: Standardize the web tier on synchronous Flask + Flask-WTF + requests

- Decision: Use Flask, Flask-WTF/WTForms, and `requests` as the canonical web-tier stack. Remove async route handling and SSE-based client behavior from the supported path.
- Rationale: The repository already has Flask and a synchronous MCP client in place. This minimizes new technology introduction and aligns with Constitution v3.0.0.
- Alternatives considered:
  - Keep Quart with compatibility shims: rejected because it still centers the web tier on an ASGI-oriented stack.
  - Use raw form parsing without Flask-WTF: rejected because the current UI already relies on form classes and CSRF-aware flows.

## Decision 7: Preserve test isolation by mocking MCP in Flask tests and exercising the wrapper separately

- Decision: Flask web-tier tests should use Flask test client plus mocked MCP client behavior, while MCP wrapper tests should validate `/rpc` contract behavior and handler integration separately.
- Rationale: This follows the constitution's boundary-aware testing rule and prevents direct database coupling inside web-tier tests.
- Alternatives considered:
  - End-to-end web tests against a real database: rejected because it violates tier isolation for the Flask suite.
  - Only unit-test the MCP wrapper internals: rejected because the new `/rpc` wrapper is an external interface and needs contract coverage.