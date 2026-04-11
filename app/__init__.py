import os
from pathlib import Path

from flask import Flask, g

from app.project_config import get_config
from app.databases.dao_mysql import MySQLDatabase
from app.databases.dao_sqllite import SQLiteDatabase


def _config_value(config_obj, key: str, default=None):
    """Read a configuration value from either a Flask config mapping or a config object."""
    if isinstance(config_obj, dict):
        return config_obj.get(key, default)
    return getattr(config_obj, key, default)


def _sqlite_db_path(config_obj) -> str:
    """Build a filesystem path for the SQLite backend from config values."""
    project_root = Path(__file__).resolve().parent.parent
    db_url = _config_value(config_obj, "DB_URL", "") or ""
    if isinstance(db_url, str) and db_url.startswith("sqlite:///"):
        raw_path = db_url.replace("sqlite:///", "", 1)
        sqlite_path = Path(raw_path)
        if not sqlite_path.is_absolute():
            sqlite_path = project_root / sqlite_path
        return str(sqlite_path.resolve())

    db_name = _config_value(config_obj, "DB_NAME", "local_db") or "local_db"
    return str((project_root / f"{db_name}.sqlite3").resolve())


def _resolve_dao_factory(config_obj):
    """Return the configured DAO class and initialization kwargs for the app."""
    backend = (_config_value(config_obj, "DB_BACKEND", "") or "").strip().lower()

    if backend and backend not in {"sqlite", "mysql"}:
        raise ValueError(f"Unsupported DB_BACKEND: {backend}. Expected 'sqlite' or 'mysql'.")

    if backend == "mysql" or (not backend and os.getenv('PYTHONANYWHERE_DOMAIN')):
        return MySQLDatabase, {
            "host": _config_value(config_obj, "DB_HOST"),
            "user": _config_value(config_obj, "DB_USER"),
            "password": _config_value(config_obj, "DB_PASSWORD"),
            "dbname": _config_value(config_obj, "DB_NAME"),
            "port": _config_value(config_obj, "DB_PORT"),
            "auth_plugin": _config_value(config_obj, "DB_AUTH_PLUGIN"),
        }

    return SQLiteDatabase, {
        "db_path": _sqlite_db_path(config_obj),
        "dbname": _config_value(config_obj, "DB_NAME", "local_db"),
    }


def create_app(test_config: dict | None = None):
    """Create and configure the Flask app with the appropriate DAO backend."""
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
        static_url_path="/static",
    )
    
    # 1. Load Configuration
    config_obj = get_config()
    app.config.from_object(config_obj)
    if test_config:
        app.config.update(test_config)
    app.secret_key = app.config["SECRET_KEY"]

    # 2. Database Provider Selection
    dao_class, dao_kwargs = _resolve_dao_factory(app.config)
    app.extensions["dao_factory"] = {
        "class": dao_class,
        "kwargs": dao_kwargs,
    }
    app.logger.info("Configured DAO backend: %s", dao_class.__name__)

    # 3. Initialization (Ensure tables exist)
    with app.app_context():
        bootstrap_db = dao_class(**dao_kwargs)
        code, err, _ = bootstrap_db.connect()
        if code != 0:
            app.logger.error(f"Database connection failed: {err}")
        else:
            schema_builders = (
                bootstrap_db.create_workflow_table,
                bootstrap_db.create_role_table,
                bootstrap_db.create_guard_table,
                bootstrap_db.create_interaction_table,
                bootstrap_db.create_interaction_component_table,
            )
            for build_schema in schema_builders:
                build_code, build_error, _ = build_schema()
                if build_code != 0:
                    app.logger.error(f"Database schema initialization failed: {build_error}")
                    break
            bootstrap_db.close()

    @app.teardown_appcontext
    def close_request_db(exception=None):
        """Close any request-scoped DAO connection stored on Flask's g object."""
        db = g.pop("db", None)
        if db is not None:
            db.close()

    # 4. Register Blueprints/Routes
    from . import routes
    app.register_blueprint(routes.bp)

    return app


app = create_app()