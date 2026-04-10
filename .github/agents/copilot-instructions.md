Project Context: Flask + MySQL + SQLite (PDFA Webservices)

🏗 General Architecture

Framework: Flask (using the App Factory pattern in app/__init__.py).

Entry Point: run.py for local development; WSGI configuration for PythonAnywhere.

Configuration: Managed via config.py and .env.

Environment Detection: The app detects PYTHONANYWHERE_DOMAIN to switch between Production (MySQL) and Development (SQLite).

📂 Database & DAO Pattern

Pattern: Custom Provider Pattern using Data Access Objects (DAO). Do not use SQLAlchemy models.

Location: All database logic is strictly contained in app/databases/.

dao_base.py: The abstract base class (BaseDAO) defining the interface.

dao_mysql.py: Implementation for MySQL (Production).

dao_sqllite.py: Implementation for SQLite (Local).

Return Contract: Every DAO method MUST return a tuple: (return_code, error_message, data).

return_code: 0 for success, -1 for failure.

error_message: None on success, string on failure.

data: Query result (list/dict/id) or None.

Constraint: Routes in app/routes.py must never execute SQL. Use current_app.db.[method]().

📝 Logging & Debugging Standards

Framework: Use the standard Python logging module within DAOs and current_app.logger within routes.

Level Configuration: Default to logging.INFO. Use logging.DEBUG for SQL query execution details (excluding sensitive data).

DAO Logging Implementation: * Every major operation (connect, insert, update, delete) must log an INFO message on start including relevant IDs (e.g., [*] [DAO START] SQLiteDatabase.insert_workflow: {name}).

Failures must be logged as ERROR including the specific exception message and context (e.g., [!] [DAO ERROR] Failed to update role {id}: {error}).

Log the connection type used (e.g., "Connected via PyMySQL fallback").

Route Logging Implementation: * Use current_app.logger.info() for request lifecycle events (e.g., [*] [ROUTE START] Accessed workflows list).

Capture "silent" failures: Use current_app.logger.error() when a DAO returns a -1 code, even if the app doesn't crash, capturing the error_message returned by the DAO.

Log incoming request parameters for critical actions (e.g., IDs for delete/update) to trace logical mismatches between the frontend and backend.

🧪 Testing Standards

Framework: pytest and pytest-flask.

Location: All tests live in the tests/ directory.

Isolation: Use sqlite:///:memory: for tests to ensure a clean slate for every run.

Requirement: When adding a new DAO method, a corresponding test case must be added to tests/test_workflows.py.

📄 Documentation (README) Rules

Automatic Sync: Keep the root README.md and app/README.md up to date.

New Folders: If a new directory is created, suggest a README.md immediately.

Logic Changes: If the DAO interface changes, update the "Usage" sections of the primary README.

⚠️ Coding Preferences

Placeholders: Use %s for MySQL queries and ? for SQLite queries.

Auth Plugin: Ensure mysql_native_password is supported to avoid caching_sha2_password errors.

Type Hinting: Use Python type hints for all function signatures and DAO methods.

Pathing: Always use relative paths or Path from pathlib for cross-platform compatibility.