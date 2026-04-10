# App Package

This directory contains the Flask application package for the project. It is structured around the Flask application factory pattern so the app can be created with environment-specific configuration and a swappable database backend.

## Purpose

The app package is responsible for:

- creating and configuring the Flask application
- registering routes and request handlers
- rendering templates and serving static assets
- delegating all persistence work to DAO implementations instead of embedding SQL in routes

## Main Files

### `__init__.py`

This file exposes `create_app()`, the application factory. It creates the Flask app, loads configuration from `config.py`, selects a database provider, performs basic startup initialization, and registers the route blueprint.

The intended flow is:

1. Create the Flask app object.
2. Load the active config class with `app.config.from_object(...)`.
3. Choose a DAO backend for the current environment.
4. Open the database connection and create required tables if needed.
5. Register blueprints and return the configured app.

### `routes.py`

This file defines the web routes using a Flask `Blueprint`. Route handlers access the active DAO through a small `get_db_provider()` helper, which reads `current_app.db` and returns the configured provider as a `BaseDAO`. That keeps the web layer tied to the DAO contract rather than to a specific backend implementation.

The Blueprint currently serves the workflow management page and exposes JSON CRUD endpoints for these entities:

- workflows
- roles
- guards
- interactions
- interaction components

### `models.py`

This file currently exists as a placeholder. If the project later introduces form objects, view models, validation helpers, or ORM-backed models, they can live here.

### `templates/`

This directory holds Jinja templates used to render HTML responses.

### `static/`

This directory holds static assets such as CSS, JavaScript, and images.

### `databases/`

This subpackage contains the DAO layer.

- `dao_base.py` defines the abstract interface shared by all backends.
- `dao_mysql.py` contains the MySQL implementation.
- `dao_sqllite.py` contains the SQLite implementation.
- `README.md` in that folder documents the DAO contract in more detail.

## Database Design Approach

The application is being organized so the Flask layer talks to a common DAO interface rather than directly to SQL statements. This gives the project two useful properties:

- routes stay small and focused on HTTP concerns
- the storage backend can change without rewriting route logic

Each DAO method follows the shared return convention:

`(return_code, error_message, data)`

By convention, `0` means success and a nonzero value means failure.

## Current Notes

The package structure now centers on the `app/databases/` DAO modules. When updating application wiring, keep imports and backend selection logic aligned with that package layout so the factory, routes, and DAO layer all reference the same implementation paths.

The current route pattern is:

- define endpoints on a Blueprint in `routes.py`
- resolve the active DAO from the Flask app context
- call only methods defined on `BaseDAO`
- handle the shared `(return_code, error_message, data)` response shape in the route layer

## Development Guidance

- Keep route functions thin and move data access into DAO classes.
- Add new database operations to `dao_base.py` first, then implement them in each backend.
- Prefer using `current_app` inside routes and initialization helpers to avoid circular imports.
- Keep templates, static assets, and persistence concerns separated by directory.