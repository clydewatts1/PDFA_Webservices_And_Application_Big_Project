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