# Feature Specification: Quart Web Tier — Phase 1 Setup (Package Skeleton & Dependencies)

**Feature Branch**: `007-quart-tier-setup`  
**Created**: 2026-03-16  
**Status**: Draft  
**Input**: User description: "Phase 1 - Quart web tier package skeleton, dependencies, and baseline configuration for the async web tier"  
**Parent Spec**: [006-web-tier-integration/spec.md](../006-web-tier-integration/spec.md)

## User Scenarios & Testing *(mandatory)*

<!--
  Phase 1 delivers the structural scaffolding that all subsequent phases depend on.
  Each story represents a discrete, independently verifiable deliverable.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Importable Quart Web Tier Package (Priority: P1)

As a developer, I need the `quart_web` package and its sub-packages to exist with correct Python module markers so that the web tier can be imported and its modules can be discovered by test runners and the application startup script.

**Why this priority**: All subsequent implementation tasks depend on the package structure existing before any module code is written. Without it, nothing can be imported, tested, or run.

**Independent Test**: Can be fully tested by:
1. Inspecting that `quart_web/__init__.py` and `quart_web/src/__init__.py` are present
2. Running `python -c "import quart_web"` and confirming no import error
3. Verifying each sub-package directory (`routes/`, `forms/`, `templates/`) has an `__init__.py` file (or is a valid template directory)
4. Confirming `quart_web/src/app.py` exists as the app factory module

**Acceptance Scenarios**:

1. **Given** a fresh checkout of the branch, **When** a developer runs `python -c "import quart_web"`, **Then** no ImportError or ModuleNotFoundError is raised
2. **Given** the package tree is in place, **When** pytest is invoked from the project root, **Then** `quart_web` modules are discovered and no collection errors occur due to missing `__init__.py` files
3. **Given** the routes sub-package skeleton exists, **When** a developer opens `quart_web/src/routes/`, **Then** all planned route modules (`health.py`, `auth.py`, `workspace.py`, `workflow.py`, `role.py`, `interaction.py`, `guard.py`, `interaction_component.py`) are present as importable stubs

---

### User Story 2 - Async Test Suite Configured and Runnable (Priority: P1)

As a developer writing async route tests, I need the pytest configuration to support async test functions without requiring per-test decorators so that the entire async test suite runs consistently from a single command.

**Why this priority**: All route and integration tests in the web tier use async functions. Without async test mode configured before any tests are written, every test written in Phase 3–8 will fail at collection or execution.

**Independent Test**: Can be fully tested by:
1. Adding a trivial `async def test_passes(): assert True` test in `quart_web/tests/unit/`
2. Running `pytest quart_web/tests/` from the project root
3. Confirming the test passes without requiring `@pytest.mark.asyncio` decorator

**Acceptance Scenarios**:

1. **Given** the pyproject.toml update is applied, **When** a developer writes `async def test_example(): assert 1 == 1` with no additional markers, **Then** pytest runs and reports the test as passed
2. **Given** both `mcp_server/` and `quart_web/` test directories exist, **When** pytest runs the full suite, **Then** async tests in both tiers pass under the shared asyncio configuration
3. **Given** a developer consults pyproject.toml, **When** reviewing test configuration, **Then** they see a single explicit `asyncio_mode = "auto"` setting scoped to the project

---

### User Story 3 - Runtime Dependencies Installable (Priority: P1)

As a developer setting up a new environment, I need the Quart web tier's runtime and development dependencies declared in the project requirement files so that running a single install command produces a working environment.

**Why this priority**: Until the correct packages are listed, the app factory cannot be imported and no integration tests can run. Dependencies must be declared before any module code references them.

**Independent Test**: Can be fully tested by:
1. Creating a fresh virtual environment
2. Running `pip install -r requirements.txt -r requirements-dev.txt`
3. Confirming `import quart`, `import quart_wtf`, `import wtforms` succeed with no errors

**Acceptance Scenarios**:

1. **Given** a clean virtual environment, **When** both requirement files are installed, **Then** `quart`, `quart-wtf`, and `wtforms` are importable at the correct versions
2. **Given** the requirements files, **When** a developer audits them, **Then** Quart runtime packages are in `requirements.txt` and test/dev packages (e.g., `pytest-asyncio`) are in `requirements-dev.txt`
3. **Given** the existing `mcp_server/` dependencies, **When** the Quart packages are added, **Then** no dependency conflicts are introduced

---

### User Story 4 - Developer Can Start the Quart Tier from Documentation (Priority: P2)

As a developer new to the project, I need README documentation that describes how to start the Quart web tier, what environment variables are required, and how the tier relates to the MCP backend so that I can run the application without consulting prior conversation logs.

**Why this priority**: While not blocking code execution, accurate startup documentation eliminates environment mistakes. It is the cheapest safety net before any further phases begin.

**Independent Test**: Can be fully tested by:
1. Following the README instructions on a machine with only the repo and a Python installation
2. Confirming the documented `quart run` (or equivalent) command starts the server
3. Verifying the README lists `MCP_SERVER_URL` and `SESSION_SECRET` as required environment variables with example values

**Acceptance Scenarios**:

1. **Given** a developer reads the project README, **When** they follow the Quart tier section, **Then** they can start the server without additional instructions
2. **Given** the README environment variable table, **When** a developer configures their `.env`, **Then** no required variable is undocumented
3. **Given** the quart_web/ directory, **When** a developer looks for a module-level README, **Then** `quart_web/README.md` exists with a brief description and startup steps

---

### Edge Cases

- What happens if `quart_web/` conflicts with an existing package name in the installed environment? (No conflict is expected; the name is project-specific.)
- What happens if `asyncio_mode = "auto"` in pyproject.toml breaks an existing synchronous test in `mcp_server/tests/`? (Assumption: existing sync tests are compatible with asyncio auto-mode; if a breakage is found, scope of fix stays within this spec.)
- What happens if a required Quart package version conflicts with an existing Flask package? (Flask and Quart are separate; no shared pinned versions are expected.)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The `quart_web` package MUST be importable from the project root without any path manipulation
- **FR-002**: Each route module stub (`health.py`, `auth.py`, `workspace.py`, `workflow.py`, `role.py`, `interaction.py`, `guard.py`, `interaction_component.py`) MUST exist under `quart_web/src/routes/` as a valid Python module
- **FR-003**: Each form module stub (`auth.py`, `workflow.py`, `role.py`, `interaction.py`, `guard.py`, `interaction_component.py`) MUST exist under `quart_web/src/forms/` as a valid Python module
- **FR-004**: All HTML template placeholders (`base.html`, `error.html`, `landing.html`, `auth/login.html`, `workspace/dashboard.html`, `workspace/entities.html`, `entities/list.html`, `entities/form.html`, `entities/delete_confirm.html`) MUST exist as valid Jinja2 skeleton files under `quart_web/src/templates/`
- **FR-005**: An `app.py` file MUST exist at `quart_web/src/app.py` providing a `create_app()` factory stub
- **FR-006**: `quart`, `quart-wtf`, and `wtforms` MUST be declared as runtime dependencies
- **FR-007**: `pytest-asyncio` MUST be declared as a development dependency
- **FR-008**: The pytest configuration MUST set `asyncio_mode = "auto"` so async test functions run without per-test markers
- **FR-009**: `quart_web/README.md` MUST document the startup command, required environment variables (`MCP_SERVER_URL`, `SESSION_SECRET`), and the relationship between the Quart tier and the MCP backend
- **FR-010**: The `quart_web/tests/` directory MUST exist with a `__init__.py` and a `unit/` sub-directory containing at least a `conftest.py` stub

### Constitutional Constraints *(mandatory when applicable)*

- **Layer boundary**: This feature creates the `quart_web/` tier — a new top-level peer to `mcp_server/` and `flask_web/`. It sits at the Web Server layer of the `Database → MCP Server → Web Server` stack. No direct database access is permitted in `quart_web/`.
- **MCP contract**: Phase 1 adds no new MCP tools and makes no changes to the MCP server contract. All MCP interaction stubs are empty placeholders; no SSE calls are issued in this phase.
- **Persistence**: This feature does not touch persistence. No SQLAlchemy models, no session logic, no temporal table modifications.
- **Isolation from flask_web/**: The `flask_web/` directory MUST NOT be modified by this feature. The two web tiers coexist independently.
- **Environment variables**: Two variables must be documented: `MCP_SERVER_URL` (default `http://127.0.0.1:5001/sse`) and `SESSION_SECRET` (required, no default). No other new variables are introduced in Phase 1.
- **Sources**: Parent spec [006-web-tier-integration/spec.md](../006-web-tier-integration/spec.md) defines the full web tier scope. Phase 1 tasks T001–T007 from [006-web-tier-integration/tasks.md](../006-web-tier-integration/tasks.md) are the authoritative task list for this spec.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 10 route, form, and template stub modules are importable with zero errors after a standard `pip install -r requirements.txt` in a clean virtual environment
- **SC-002**: Running `pytest quart_web/tests/` with a single trivial async test function passes in under 5 seconds with no collection warnings about missing asyncio configuration
- **SC-003**: A developer with no prior context can start the Quart tier within 5 minutes by following the README alone, with no failed steps due to undocumented prerequisites
- **SC-004**: Adding the Quart runtime dependencies produces zero pip dependency conflicts with the existing `mcp_server/` requirements

## Assumptions

- `quart` and `flask` can coexist in the same virtual environment (confirmed: they share no pinned conflicting dependencies on current versions)
- The project root is a Python package root; `quart_web/` at the top level will be discovered by pytest without additional `conftest.py` path manipulation
- Existing `mcp_server/` tests do not use synchronous fixtures that would break under `asyncio_mode = "auto"` — if they do, fixing those tests is out of scope for this spec
- Stub template files may contain minimal placeholder content (e.g., `{% extends "base.html" %}`) rather than production HTML; full template implementation is deferred to Phases 3–8
- Stub Python modules may contain only a module docstring and a `# TODO` comment; no real route or form logic is written in Phase 1
