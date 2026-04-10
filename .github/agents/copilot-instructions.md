# Project Context: Flask + MySQL + SQLite

## General Tech Stack
- **Framework:** Flask
- **Primary Database (Production):** MySQL (using `mysql-connector-python`)
- **Secondary Database (Local/Testing):** SQLite
- **ORM/Interface:** [Specify if using SQLAlchemy or raw SQL. Example: SQLAlchemy]

## Architecture Patterns
- Follow a Factory Pattern for app initialization (`create_app()`).
- Separate database schemas from routes using a `models.py` or a `database/` directory.
- Use Environment Variables (`.env`) for database credentials.

## Database Guidelines
- **Switching Logic:** Always check for `FLASK_ENV`. Use SQLite for development/testing and MySQL for production.
- **SQL Syntax:** When writing raw SQL, prioritize standard ANSI SQL to maintain compatibility between SQLite and MySQL where possible.
- **Error Handling:** Use `mysql.connector.errors` for MySQL-specific exceptions and standard `sqlite3.Error` for SQLite.

## Code Style & Preferences
- Use Type Hinting for all function signatures.
- Prefer `f-strings` for string formatting.
- Implement Flask Blueprints to keep the codebase modular.
- Always include basic docstrings for new routes explaining the expected JSON payload and response codes.

## Database Architecture & DAO Pattern
Pattern: This project uses a Provider Pattern with a Data Access Object (DAO) instead of Flask-SQLAlchemy.

Location: All database logic is located in app/database/.

base_dao.py: Contains the abstract BaseDAO class defining the interface.

mysql_dao.py: Implementation for Production/PythonAnywhere using mysql.connector or pymysql.

sqlite_dao.py: Implementation for Local Development using sqlite3.

###🛠 DAO Implementation Rules
No SQL in Routes: Routes must never execute SQL. They must call methods from the DAO instance attached to the Flask app (e.g., current_app.db.method_name()).

Consistent Returns: Every DAO method must return a tuple: (return_code, error_message, data).

return_code: 0 for success, -1 for failure.

error_message: None on success, a string description on failure.

data: The result (list, dict, or ID) or None.

Inheritance: When adding new methods, add the signature to BaseDAO first, then implement it in both mysql_dao.py and sqlite_dao.py.

### ⚠️ SQL Syntax Specifics
Placeholders: - Use %s for mysql_dao.py.

Use ? for sqlite_dao.py.

Primary Keys: - Use INT AUTO_INCREMENT for MySQL.

Use INTEGER PRIMARY KEY AUTOINCREMENT for SQLite.

Connections: Always use the ensure_connection() or ping() logic provided in the DAO classes to handle timeouts, especially for PythonAnywhere.

##📄 Documentation & README Standards
Proactive Creation: If a new module or directory is created and lacks a README.md, immediately suggest a baseline README that explains the directory's purpose.

Continuous Updates: Whenever a new route is added to routes.py or a new method is added to the DAO classes, prompt the user to update the root README.md to reflect these changes.

Technical Stack Transparency: Every README must explicitly mention the dual-database setup (SQLite for local, MySQL for PythonAnywhere) and the custom DAO pattern.

### README Template: Ensure READMEs include:

Purpose: What this specific folder/project does.

Setup: Any specific .env keys required.

Usage: Example of how to call the primary functions or routes.

DAO Reference: A reminder that no raw SQL should be written outside the /database folder.