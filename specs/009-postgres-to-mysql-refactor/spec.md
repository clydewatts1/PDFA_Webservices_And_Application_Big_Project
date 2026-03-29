# Feature Specification: Refactor Database Driver from PostgreSQL to MySQL

**Feature Branch**: `009-postgres-to-mysql-refactor`  
**Created**: 2026-03-23  
**Status**: Draft  
**Input**: User description: "refactor from postgress to mysql"

## Clarifications and Decisions

- Q: Which MySQL Python driver should be used? → A: PyMySQL (`mysql+pymysql://`), as it is pure-Python and requires no native binary installation, keeping local developer setup simple.
- Q: Should SQLite remain the path for automated tests? → A: Yes. The existing contract and integration test suites use SQLite in-process for isolation; this refactor does not change that pattern.
- Q: Are there any PostgreSQL-specific column types or sequences in the current schema that require dialect-specific migration? → A: The current SQLAlchemy models use `String`, `DateTime`, `Integer`, and `Boolean`, which are all MySQL-compatible. No PostgreSQL-specific types (e.g., `ARRAY`, `JSONB`, `UUID`) are present.

### Session 2026-03-23

- Q: Are schema migration changes required for this feature? → A: No. This feature is limited to driver/configuration and documentation updates; schema migration changes are out of scope.
- Q: Should the MySQL connection string include `charset=utf8mb4` to ensure correct handling of multi-byte characters across all SCD string columns? → A: Yes — all `DB_URL` examples MUST append `?charset=utf8mb4`. This is mandatory for MySQL 8.x to prevent silent data corruption in string columns used by SCD temporal audit fields.
- Q: Should `session.py` be updated to add `pool_recycle` and `pool_pre_ping` parameters to avoid stale connections from MySQL's default 8-hour session timeout? → A: Yes — `create_engine()` MUST be called with `pool_recycle=3600` and `pool_pre_ping=True` to prevent "MySQL server has gone away" errors in long-running MCP server deployments.
- Q: Should SSL/TLS parameters be specified for MySQL connections? → A: No — SSL/TLS configuration is out of scope for this feature; the deployment environment is responsible for transport security.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Configures MySQL Connection (Priority: P1)

A developer running the project locally or in a deployment environment sets `DB_URL` to a MySQL connection string and starts the MCP server without errors. All existing workflow table operations (create, read, update, SCD history write) continue to behave identically.

**Why this priority**: This is the core deliverable — without a working MySQL connection, nothing else in this refactor has value.

**Independent Test**: Can be fully tested by setting `DB_URL=mysql+pymysql://...` then starting the MCP server and calling the `get_system_health` tool. Delivers a fully connected MySQL-backed MCP server.

**Acceptance Scenarios**:

1. **Given** a MySQL database instance is running and `DB_URL` is set to a valid `mysql+pymysql://` connection string, **When** the MCP server starts, **Then** it reports a healthy database status via the `get_system_health` tool with no connection errors.
2. **Given** a valid `DB_URL` pointing to MySQL, **When** the MCP server starts, **Then** database connectivity is successful and no driver-related startup error occurs.
3. **Given** the MCP server is connected to MySQL, **When** `get_system_health` is called, **Then** it reports healthy database status.

---

### User Story 2 - Existing Tests Continue to Pass (Priority: P2)

A developer runs the automated test suite after the refactor. All existing contract and integration tests pass using SQLite in-process without modification.

**Why this priority**: Preserving test isolation ensures the refactor introduces no regressions and that tier boundaries remain intact.

**Independent Test**: Running `pytest mcp_server/tests/` in isolation delivers confirmation that no test is broken by the driver change.

**Acceptance Scenarios**:

1. **Given** the codebase has been updated to use the MySQL driver, **When** the full test suite is executed, **Then** all previously passing tests pass without modification.
2. **Given** a test fixture that uses SQLite in-process via `DB_URL`, **When** a test creates and updates a domain entity, **Then** the SCD Type-2 history write is verified as before — the MySQl driver change does not affect test-time SQLite behavior.

---

### User Story 3 - Documentation Updated to Reflect MySQL (Priority: P3)

A developer or reviewer reads project documentation — quickstart guides, README files, and spec artifacts — and finds MySQL connection string examples and driver references everywhere PostgreSQL was previously referenced.

**Why this priority**: Documentation accuracy matters for onboarding and grading traceability, but does not block runtime functionality.

**Independent Test**: Can be fully verified by searching all `*.md` files for PostgreSQL references and confirming each is updated or annotated to reflect MySQL.

**Acceptance Scenarios**:

1. **Given** the refactor is complete, **When** a reviewer searches project documentation for "postgresql" or "psycopg", **Then** all remaining occurrences are either historical references in old spec artifacts (marked read-only) or appropriately replaced with MySQL equivalents.
2. **Given** the quickstart guides reference `DB_URL` examples, **When** a developer copies the example value, **Then** it uses a `mysql+pymysql://` connection string format.

---

### Edge Cases

- What happens when the MySQL server is unreachable at startup? The MCP server MUST surface a clear error via `get_system_health` — identical behavior to the current missing `DB_URL` guard already in `system_service.py`.
- What happens if `DB_URL` contains a `postgresql://` prefix after the refactor? The session factory will raise a connection error at runtime; the deployment guide must document that the old URL format is no longer valid.
- What happens to the SQLite test path? SQLite URLs (`sqlite:///...`) remain unaffected; test fixtures continue to use SQLite without change.
- What happens if `charset=utf8mb4` is omitted from `DB_URL`? MySQL may silently truncate or mangle multi-byte characters in `InsertUserName`, `UpdateUserName`, and other `String` SCD columns, causing data corruption that is not immediately visible. Including `?charset=utf8mb4` in the URL is therefore mandatory.
- What happens if `pool_pre_ping=True` is omitted? After MySQL's default 8-hour `wait_timeout`, idle connections in the pool become stale. The next query will raise `OperationalError: (2006, 'MySQL server has gone away')`. Setting `pool_recycle=3600, pool_pre_ping=True` prevents this.

## Layer Partition *(mandatory)*

### MCP (Logic)

**Scope**: All database connectivity changes are contained within the MCP server tier. No other tier is affected.

**Responsibilities**:
- Update `requirements.txt` to replace any PostgreSQL driver (`psycopg`, `psycopg2`) with `PyMySQL>=1.1,<2.0`.
- Update `mcp_server/src/db/session.py` to pass `pool_recycle=3600` and `pool_pre_ping=True` to `create_engine()`. The `DB_URL` env var path is already correct; only the engine keyword arguments change.
- No schema migration scripts, migration environment files, or Alembic configuration are changed in this feature.
- Update all `DB_URL` examples in documentation to use `mysql+pymysql://user:password@host:3306/dbname?charset=utf8mb4`.

**Boundary constraints**: SQLAlchemy and PyMySQL MUST remain confined to the MCP server tier. The Quart web tier MUST NOT be modified as part of this feature.

**Affected contracts**: No MCP tool contracts (JSON-RPC) change. The `get_system_health` tool's response shape is unchanged; only the backing database engine differs.

---

### Web-Tier (Routes)

**Scope**: No changes required.

The Quart web server communicates with the MCP server exclusively via HTTP. It has no awareness of the database driver or connection string. This layer is unaffected by this refactor.

---

### Page (UI)

**Scope**: No changes required.

No UI templates, forms, or Jinja context processors reference the database driver or connection configuration. This layer is unaffected by this refactor.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The project MUST use `PyMySQL` as the MySQL Python driver, specified in `requirements.txt`.
- **FR-002**: The `DB_URL` environment variable MUST accept a `mysql+pymysql://` connection string and the MCP server MUST connect successfully to MySQL using it.
- **FR-003**: This feature MUST NOT require schema migration changes; migration files and migration infrastructure remain out of scope.
- **FR-004**: The `get_system_health` MCP tool MUST return `status="ok"` when MySQL is reachable, and MUST return `status="error"` with an error message containing at least one of: `unable to connect`, `connection refused`, or `OperationalError` when MySQL is unreachable.
- **FR-005**: The automated test suite MUST continue to pass using SQLite in-process for all contract and integration tests without modification.
- **FR-006**: All quickstart documentation and `DB_URL` examples MUST reference `mysql+pymysql://` format connection strings and MUST include `?charset=utf8mb4` to prevent multi-byte character encoding failures.
- **FR-007**: Documentation search for "psycopg" and "postgresql+psycopg" across current-branch files MUST return zero results outside of historical/read-only spec artifacts. Allowed residual matches MUST be restricted to the explicit allowlist documented in `specs/009-postgres-to-mysql-refactor/research.md`.
- **FR-008**: The `create_engine()` call in `mcp_server/src/db/session.py` MUST include `pool_recycle=3600` and `pool_pre_ping=True` to prevent stale connection errors from MySQL's default 8-hour `wait_timeout`.
- **FR-009**: SSL/TLS configuration for MySQL connections is out of scope; the deployment environment is responsible for transport security.

### Key Entities

- **DB_URL**: The single environment variable controlling database connectivity. Its value format changes from `postgresql+psycopg://...` to `mysql+pymysql://...`. No application code outside the `DB_URL` value needs to change because SQLAlchemy abstracts the dialect.
- **PyMySQL**: The replacement Python library that provides the MySQL dialect adapter for SQLAlchemy. Pure-Python, no native compilation required.

### Assumptions

- The current SQLAlchemy models use only generic column types (`String`, `Integer`, `DateTime`, `Boolean`) and no PostgreSQL-specific types. This was verified by inspection.
- The test suite exclusively uses SQLite for fixtures, so no test database connection strings need updating.
- A MySQL 8.x instance is the target. MySQL 5.7 is not a supported target because it has significant UTF-8 and datetime precision limitations.
- The MySQL server is configured with `default_authentication_plugin=mysql_native_password` or `caching_sha2_password` (MySQL 8.x default); PyMySQL 1.1+ supports both.
- The `?charset=utf8mb4` query parameter in `DB_URL` is the client-side declaration; the MySQL server and database are assumed to be created with `CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci`.

### Constitutional Constraints

- **Three-Tier Boundary**: This feature touches only the Database and MCP Server tiers. The Quart web server tier is unaffected. The Database → MCP → Quart boundary remains intact.
- **SQLAlchemy Containment**: SQLAlchemy and the new PyMySQL driver remain confined entirely to the MCP server tier as required by Principle III. The Quart tier imports no database libraries.
- **SCD Type-2 Integrity**: No changes are made to current or `_Hist` table structures, temporal columns (`EffFromDateTime`, `EffToDateTime`, `DeleteInd`, `InsertUserName`, `UpdateUserName`), or the MCP-owned history orchestration logic. The database driver change is transparent to SCD behavior.
- **MCP Contracts**: No MCP tool signatures, JSON-RPC method names, or SSE event shapes change. The driver replacement is an infrastructure concern only.
- **Workflow Schema Integrity**: The seven-table schema (Workflow, Role, Interaction, Guard, InteractionComponent, UnitOfWork, Instance) and their `_Hist` counterparts are preserved without structural modification.
- **Required Environment Variable Change**:
  - `DB_URL` must be updated from `postgresql+psycopg://user:password@host:5432/dbname` to `mysql+pymysql://user:password@host:3306/dbname?charset=utf8mb4`
  - The `?charset=utf8mb4` suffix is mandatory to ensure correct multi-byte character handling in all SCD string audit columns.
- **External Source Attribution**: This specification was produced with GitHub Copilot (Claude Sonnet 4.6) assistance via Spec Kit `/speckit.specify` on 2026-03-23.
- **Documentation Expectations**: `specs/001-define-workflow-tables/quickstart.md` and `docs/mcp_milestone_test_guide.md` contain PostgreSQL URL examples that must be updated. The root README and each tier README should be reviewed for any DB_URL examples.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The MCP server starts and reports a healthy database status when pointed at a running MySQL instance via `DB_URL`.
- **SC-002**: With a valid MySQL `DB_URL`, the MCP server starts without driver-related errors.
- **SC-003**: 100% of previously passing automated tests continue to pass after the driver change, with no test fixture modifications required.
- **SC-004**: Zero occurrences of `psycopg` or `postgresql+psycopg` appear in any file under active development (excluding read-only spec artifacts from features 001–008).
- **SC-005**: Developer documentation clearly shows MySQL-based setup steps and valid `DB_URL` examples.
- **SC-006**: All `DB_URL` examples in documentation include `?charset=utf8mb4` and the `mcp_server/src/db/session.py` `create_engine()` call includes `pool_recycle=3600` and `pool_pre_ping=True`.
- **SC-007**: No schema migration changes are introduced by this feature.
