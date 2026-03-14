"""Flask web application entrypoint for temporary Section V demo flows."""

from __future__ import annotations

import json
import logging
import os

from flask import Flask, jsonify

from flask_web.src.clients.mcp_client import MCPClientError
from flask_web.src.routes.dependent import dependent_bp
from flask_web.src.routes.instance import instance_bp
from flask_web.src.routes.workflow import workflow_bp


logger = logging.getLogger("pdfa.flask")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


def create_app() -> Flask:
    """Create and configure the Flask web application instance."""

    app = Flask(__name__)

    app.register_blueprint(workflow_bp)
    app.register_blueprint(dependent_bp)
    app.register_blueprint(instance_bp)

    @app.get("/")
    def index():
        """Render the top-level navigation index page."""

        return (
            "<h1>PDFA Temporary App</h1>"
            "<ul>"
            "<li><a href='/workflow'>Workflow</a></li>"
            "<li><a href='/entities/role'>Dependent Entities</a></li>"
            "<li><a href='/instance'>Instances</a></li>"
            "</ul>"
        )

    @app.errorhandler(MCPClientError)
    def handle_mcp_client_error(error: MCPClientError):
        """Normalize MCP client exceptions into JSON HTTP responses."""

        logger.warning(
            json.dumps(
                {
                    "event": "flask.mcp.error",
                    "code": error.code,
                    "message": error.message,
                    "data": error.data,
                }
            )
        )
        return jsonify({"error": {"code": error.code, "message": error.message, "data": error.data}}), 502

    return app


app = create_app()


if __name__ == "__main__":
    """Run the Flask app using environment-driven host and port values."""

    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5000"))
    app.run(host=host, port=port, debug=False)
