import os

from flask import Flask

from app.project_config import get_config
from app.databases.dao_mysql import MySQLDatabase
from app.databases.dao_sqllite import SQLiteDatabase


def _sqlite_db_path(config_obj) -> str:
    """Build a filesystem path for the SQLite backend from config values."""
    db_url = getattr(config_obj, "DB_URL", "") or ""
    if isinstance(db_url, str) and db_url.startswith("sqlite:///"):
        return db_url.replace("sqlite:///", "", 1)

    db_name = getattr(config_obj, "DB_NAME", "local_db") or "local_db"
    return f"{db_name}.sqlite3"

def create_app():
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

    # 2. Database Provider Selection
    # PythonAnywhere automatically sets 'PYTHONANYWHERE_DOMAIN'
    if os.getenv('PYTHONANYWHERE_DOMAIN'):
        app.logger.info("Environment: PythonAnywhere detected. Using MySQL.")
        #app.db = MySQLDatabase(
        #    host=config_obj.DB_HOST,
        #    user=config_obj.DB_USER,
        #    password=config_obj.DB_PASSWORD,
        #    dbname=config_obj.DB_NAME,
        #    port=config_obj.DB_PORT,
        #    auth_plugin=getattr(config_obj, 'DB_AUTH_PLUGIN', None)
        #)
        # user sqllite for now to avoid auth plugin issues on PA
        app.logger.warning(
            "MySQL configuration is present but using SQLite for now due to auth plugin issues."
        )
        app.db = SQLiteDatabase(
            db_path=_sqlite_db_path(config_obj),
            dbname=config_obj.DB_NAME,
        )

    else:
        app.logger.info("Environment: Local Laptop detected. Using SQLite.")
        app.db = SQLiteDatabase(
            db_path=_sqlite_db_path(config_obj),
            dbname=config_obj.DB_NAME,
        )

    # 3. Initialization (Ensure tables exist)
    # Note: connect() inside your DAO should handle the heavy lifting
    with app.app_context():
        # Test connection and initialize tables if they don't exist
        code, err, _ = app.db.connect()
        if code != 0:
            app.logger.error(f"Database connection failed: {err}")
        else:
            schema_builders = (
                app.db.create_workflow_table,
                app.db.create_role_table,
                app.db.create_guard_table,
                app.db.create_interaction_table,
                app.db.create_interaction_component_table,
            )
            for build_schema in schema_builders:
                build_code, build_error, _ = build_schema()
                if build_code != 0:
                    app.logger.error(f"Database schema initialization failed: {build_error}")
                    break

    # 4. Register Blueprints/Routes
    from . import routes
    app.register_blueprint(routes.bp)

    return app


app = create_app()