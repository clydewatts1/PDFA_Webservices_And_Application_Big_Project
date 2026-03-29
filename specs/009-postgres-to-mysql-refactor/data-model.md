# Data Model: Refactor Database Driver from PostgreSQL to MySQL

**Feature**: 009-postgres-to-mysql-refactor  
**Date**: 2026-03-23

## Schema Changes

**None.** This feature is a database driver replacement. No table structures, column
definitions, relationships, constraints, or indexes are added, removed, or modified.

The full seven-table workflow schema and its symmetric `_Hist` counterparts are preserved
exactly as created by migration `0001_current_history_tables.py`.

---

## Existing Schema Summary (reference only — unchanged)

| Table | `_Hist` Counterpart | PK | Notable Columns |
|-------|--------------------|----|-----------------|
| `Workflow` | `Workflow_Hist` | `id` (AUTO_INCREMENT) | `WorkflowName` (UNIQUE), SCD columns |
| `Role` | `Role_Hist` | `id` | `RoleName`, `WorkflowName` |
| `Interaction` | `Interaction_Hist` | `id` | `InteractionName`, `WorkflowName` |
| `Guard` | `Guard_Hist` | `id` | `GuardName`, `WorkflowName` |
| `InteractionComponent` | `InteractionComponent_Hist` | `id` | `InteractionComponentName` |
| `UnitOfWork` | `UnitOfWork_Hist` | `id` | `UnitOfWorkID` (UNIQUE) |
| `Instance` | `Instance_Hist` | `id` | `InstanceName` (UNIQUE), `WorkflowName` |

All 14 tables carry the five mandatory SCD Type-2 temporal/audit columns:

| Column | Type | Notes |
|--------|------|-------|
| `EffFromDateTime` | `DATETIME` (MySQL) | NOT NULL |
| `EffToDateTime` | `DATETIME` (MySQL) | NOT NULL |
| `DeleteInd` | `INT` | NOT NULL, DEFAULT 0 |
| `InsertUserName` | `VARCHAR(128)` | NOT NULL |
| `UpdateUserName` | `VARCHAR(128)` | NOT NULL |

---

## MySQL Dialect Mapping (from SQLAlchemy generic types)

| SQLAlchemy Type | MySQL DDL | Notes |
|-----------------|-----------|-------|
| `Integer()` | `INT` | AUTO_INCREMENT applied automatically when sole PK |
| `String(128)` | `VARCHAR(128)` | charset=utf8mb4 enforced via connection URL |
| `Text()` | `LONGTEXT` | MySQL maps `Text()` to `LONGTEXT` |
| `DateTime()` | `DATETIME` | MySQL DATETIME supports microseconds in 8.x |
| `sa.Identity(always=False)` | *(silently ignored)* | AUTO_INCREMENT from PrimaryKeyConstraint |
| `server_default=sa.text("0")` | `DEFAULT 0` | Compatible with MySQL |

---

## Migration File Status

- `database/migrations/versions/0001_current_history_tables.py`: **No changes required.**
  See `research.md` Task 1 for detailed rationale.

---

## Code Changes to Session Layer

The only runtime code change is in `mcp_server/src/db/session.py`:

**Before**:
```python
engine = create_engine(url, connect_args={"check_same_thread": False} if "sqlite" in url else {})
```

**After**:
```python
engine = create_engine(
    url,
    connect_args={"check_same_thread": False} if "sqlite" in url else {},
    pool_recycle=3600,
    pool_pre_ping=True,
)
```

`pool_recycle` and `pool_pre_ping` are harmless for SQLite (test path) and provide MySQL
connection-pool reliability for production. No state or schema is affected by this change.
