"""Load configuration for the app package without depending on sys.path."""

import os
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace

from dotenv import load_dotenv


def _load_dotenv_from(project_root: Path) -> None:
    """Load a project-level .env file when one is available."""
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)


def _build_fallback_module(project_root: Path) -> SimpleNamespace:
    """Return an in-package fallback config module when config.py is absent."""
    _load_dotenv_from(project_root)

    class Config:
        SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-123")
        DB_PORT = os.getenv("DB_PORT", 3306)
        DB_AUTH_PLUGIN = os.getenv("DB_AUTH_PLUGIN", "mysql_native_password")

    class DevelopmentConfig(Config):
        DEBUG = True
        #DB_URL = "sqlite:///local.db"
        # Placeholder values for local init
        # Use memor for testing to avoid file permissions issues on PA
        DB_URL = "sqlite:///:memory:"
        DB_HOST = "localhost"
        DB_USER = "root"
        DB_PASSWORD = ""
        DB_NAME = "local_db"

    class ProductionConfig(Config):
        DEBUG = False
        DB_HOST = os.getenv("DB_HOST")
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_NAME = os.getenv("DB_NAME")
        DB_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

    def get_config():
        if os.getenv("PYTHONANYWHERE_DOMAIN"):
            return ProductionConfig
        return DevelopmentConfig

    return SimpleNamespace(get_config=get_config)


def _load_config_module(config_path: Path | None = None):
    """Load the root-level config.py module, or fall back to package-local defaults."""
    project_root = Path(__file__).resolve().parent.parent
    config_path = config_path or (project_root / "config.py")

    if not config_path.exists():
        return _build_fallback_module(project_root)

    module_spec = spec_from_file_location("project_root_config", config_path)
    if module_spec is None or module_spec.loader is None:
        return _build_fallback_module(project_root)

    _load_dotenv_from(project_root)
    config_module = module_from_spec(module_spec)
    module_spec.loader.exec_module(config_module)
    return config_module


_CONFIG_MODULE = _load_config_module()
get_config = _CONFIG_MODULE.get_config
