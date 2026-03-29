"""Health-check route — stub (Phase 1 skeleton).

US1: GET / calls MCP get_system_health and renders landing.html.
Implementation deferred to Phase 3 (T018–T021).
"""

from __future__ import annotations

import json
import logging
import time

from quart import Blueprint, current_app, render_template, session


health_bp = Blueprint("health", __name__)

logger = logging.getLogger("pdfa.quart.health")


@health_bp.get("/")
async def landing():
	"""Render landing page with MCP health status and login enablement state."""
	started = time.perf_counter()
	health_payload: dict = {}
	is_healthy = False
	error_message = ""

	try:
		health_payload = await current_app.mcp_client.call_tool("get_system_health", {})
		health_status = str(health_payload.get("health_status", "")).upper()
		is_healthy = health_status in {"CONNECTED", "HEALTHY", "UP", "OK"}
		if not is_healthy and health_payload.get("status") == "success":
			is_healthy = True
	except Exception as exc:
		error_message = str(exc)
		health_payload = {
			"status": "error",
			"health_status": "UNAVAILABLE",
			"health_status_description": "The backend is currently unavailable.",
		}

	duration_ms = round((time.perf_counter() - started) * 1000, 2)
	logger.info(
		json.dumps(
			{
				"event": "quart.health.check.completed",
				"tool_name": "get_system_health",
				"duration_ms": duration_ms,
				"workflow_name": session.get("active_workflow_name"),
				"username": session.get("user_id"),
				"is_healthy": is_healthy,
				"error": error_message,
			}
		)
	)

	return await render_template(
		"landing.html",
		is_healthy=is_healthy,
		health_payload=health_payload,
		health_error=error_message,
	)
