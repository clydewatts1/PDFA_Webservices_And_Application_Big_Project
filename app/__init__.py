import os
from flask import Flask
from config import get_config
from app.database.mysql_dao import MySQLDAO
from app.database.sqlite_dao import SQLiteDAO

def create_app():
    """
    Flask App Factory. 
    Detects environment and initializes the correct DAO (MySQL or SQLite).
    """
    app = Flask(__name__)
    
    # 1. Load Configuration
    config_obj = get_config()
    app.config.from_object(config_obj)

    # 2. Database Provider Selection
    # PythonAnywhere automatically sets 'PYTHONANYWHERE_DOMAIN'
    if os.getenv('PYTHONANYWHERE_DOMAIN'):
        app.logger.info("Environment: PythonAnywhere detected. Using MySQL.")
        app.db = MySQLDAO(config_obj)
    else:
        app.logger.info("Environment: Local Laptop detected. Using SQLite.")
        app.db = SQLiteDAO(config_obj)

    # 3. Initialization (Ensure tables exist)
    # Note: connect() inside your DAO should handle the heavy lifting
    with app.app_context():
        # Test connection and initialize tables if they don't exist
        code, err, _ = app.db.connect()
        if code != 0:
            app.logger.error(f"Database connection failed: {err}")
        else:
            # You can trigger table creation here
            app.db.create_workflow_table()

    # 4. Register Blueprints/Routes
    from . import routes
    app.register_blueprint(routes.bp)

    return app