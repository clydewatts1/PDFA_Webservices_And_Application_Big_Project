"""Blueprint registrations and route utilities for the Quart web tier."""

from quart_web.src.routes.auth import auth_bp
from quart_web.src.routes.guard import guard_bp
from quart_web.src.routes.health import health_bp
from quart_web.src.routes.interaction import interaction_bp
from quart_web.src.routes.interaction_component import interaction_component_bp
from quart_web.src.routes.role import role_bp
from quart_web.src.routes.workflow import workflow_bp
from quart_web.src.routes.workspace import workspace_bp

__all__ = [
	"health_bp",
	"auth_bp",
	"workspace_bp",
	"workflow_bp",
	"role_bp",
	"interaction_bp",
	"guard_bp",
	"interaction_component_bp",
]
