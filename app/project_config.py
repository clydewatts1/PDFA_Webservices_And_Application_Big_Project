"""Load the project configuration module from inside the app package."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def _load_config_module():
    """Load the root-level config.py module without relying on sys.path."""
    config_path = Path(__file__).resolve().parent.parent / "config.py"
    module_spec = spec_from_file_location("project_root_config", config_path)
    if module_spec is None or module_spec.loader is None:
        raise ModuleNotFoundError(f"Unable to load configuration module from {config_path}")

    config_module = module_from_spec(module_spec)
    module_spec.loader.exec_module(config_module)
    return config_module


_CONFIG_MODULE = _load_config_module()
get_config = _CONFIG_MODULE.get_config
