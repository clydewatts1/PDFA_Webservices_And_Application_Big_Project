# Database DAO Package

This package defines the data-access layer used by the app package. The goal is to keep database-specific code out of routes and higher-level application logic by exposing a common DAO contract and backend-specific implementations.

`dao_base.py` contains `BaseDAO`, the abstract interface that all concrete DAO implementations must satisfy. It defines the connection lifecycle, schema helpers, and CRUD-style methods for workflows, roles, guards, interactions, and interaction components.

`dao_mysql.py` provides the MySQL implementation. It is written around `mysql-connector-python`, with a `PyMySQL` fallback for environments where the connector cannot negotiate the configured authentication plugin. This backend is the closer match to the original project DAO behavior.

`dao_sqllite.py` provides a SQLite implementation of the same contract. It is useful for local development, lightweight testing, and in-memory smoke tests where bringing up MySQL is unnecessary. The filename currently uses the existing project spelling `sqllite` so it stays consistent with the repository.

Across both implementations, methods return a tuple in the form `(return_code, error_message, data)`. A `return_code` of `0` indicates success. A nonzero value indicates failure, with `error_message` explaining the problem and `data` set to the relevant payload or an empty fallback.

When extending this package:

- Add new abstract methods to `BaseDAO` first.
- Implement the same method in each concrete backend.
- Keep route handlers and service logic dependent on the interface, not on backend-specific SQL details.
- Preserve the shared return convention so callers can switch backends without rewriting control flow.
