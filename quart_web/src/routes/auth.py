"""Authentication routes — stub (Phase 1 skeleton).

US2: GET /login, POST /login, POST /logout via MCP user_logon/user_logoff.
Implementation deferred to Phase 4 (T026–T029).
"""

from __future__ import annotations

import json
import logging
import secrets
import time

from quart import Blueprint, current_app, flash, redirect, render_template, request, session
from werkzeug.datastructures import MultiDict

from quart_web.src.clients.errors import MCPClientError
from quart_web.src.forms.auth import LoginForm


auth_bp = Blueprint("auth", __name__)

logger = logging.getLogger("pdfa.quart.auth")


def _get_or_create_csrf_token() -> str:
	csrf_token = str(session.get("_csrf_token") or "")
	if not csrf_token:
		csrf_token = secrets.token_urlsafe(32)
		session["_csrf_token"] = csrf_token
	return csrf_token


def _is_csrf_valid(submitted_token: str | None) -> bool:
	if not current_app.config.get("WTF_CSRF_ENABLED", True):
		return True
	session_token = str(session.get("_csrf_token") or "")
	return bool(session_token) and secrets.compare_digest(session_token, str(submitted_token or ""))


def _login_form_with_token(form_data: MultiDict | None = None, csrf_token: str | None = None) -> LoginForm:
	form = LoginForm(form_data)
	form.csrf_token.data = csrf_token if csrf_token is not None else _get_or_create_csrf_token()
	return form


@auth_bp.get("/login")
async def get_login():
	"""Render login page."""
	if session.get("user_id"):
		return redirect("/dashboard")
	form = _login_form_with_token(csrf_token=_get_or_create_csrf_token())
	return await render_template("auth/login.html", form=form)


@auth_bp.post("/login")
async def post_login():
	"""Authenticate user via MCP user_logon tool and establish session."""
	started = time.perf_counter()
	form_data = MultiDict(await request.form)
	username = str(form_data.get("username") or "")
	if not _is_csrf_valid(form_data.get("csrf_token")):
		return "Bad Request", 400

	form = _login_form_with_token(form_data, csrf_token=_get_or_create_csrf_token())

	if not form.validate():
		logger.info(
			json.dumps(
				{
					"event": "quart.auth.login.validation_failed",
					"tool_name": "user_logon",
					"duration_ms": round((time.perf_counter() - started) * 1000, 2),
					"workflow_name": session.get("active_workflow_name"),
					"username": username,
					"errors": form.errors,
				}
			)
		)
		return await render_template("auth/login.html", form=form), 200

	username = form.username.data or username
	try:
		result = await current_app.mcp_client.call_tool(
			"user_logon",
			{"username": username, "password": form.password.data or ""},
		)
	except MCPClientError as exc:
		logger.warning(
			json.dumps(
				{
					"event": "quart.auth.login.mcp_error",
					"tool_name": "user_logon",
					"duration_ms": round((time.perf_counter() - started) * 1000, 2),
					"workflow_name": session.get("active_workflow_name"),
					"username": username,
					"error": exc.message,
					"status_code": getattr(exc, "status_code", 502),
				}
			)
		)
		await flash("Authentication service is unavailable. Please try again.", "danger")
		form = _login_form_with_token(csrf_token=_get_or_create_csrf_token())
		return await render_template("auth/login.html", form=form), 200

	status = str(result.get("status", "")).upper()
	duration_ms = round((time.perf_counter() - started) * 1000, 2)

	if status == "SUCCESS":
		actor = str(result.get("username", username))
		session["user_id"] = actor
		session.pop("active_workflow_name", None)
		logger.info(
			json.dumps(
				{
					"event": "quart.auth.login.success",
					"username": actor,
					"duration_ms": duration_ms,
					"tool_name": "user_logon",
					"workflow_name": session.get("active_workflow_name"),
				}
			)
		)
		return redirect("/dashboard")

	message = str(result.get("status_message") or result.get("ErrorMessage") or "Login denied")
	logger.info(
		json.dumps(
			{
				"event": "quart.auth.login.denied",
				"username": username,
				"duration_ms": duration_ms,
				"tool_name": "user_logon",
				"workflow_name": session.get("active_workflow_name"),
				"reason": message,
			}
		)
	)
	await flash(message, "danger")
	form = _login_form_with_token(csrf_token=_get_or_create_csrf_token())
	return await render_template("auth/login.html", form=form), 200


@auth_bp.post("/logout")
async def post_logout():
	"""Log user out via MCP user_logoff and clear session."""
	form_data = MultiDict(await request.form)
	if not _is_csrf_valid(form_data.get("csrf_token")):
		return "Bad Request", 400

	username = session.get("user_id")
	if not username:
		return redirect("/login")

	started = time.perf_counter()
	try:
		await current_app.mcp_client.call_tool("user_logoff", {"username": username})
	except MCPClientError as exc:
		logger.warning(
			json.dumps(
				{
					"event": "quart.auth.logout.mcp_error",
					"tool_name": "user_logoff",
					"duration_ms": round((time.perf_counter() - started) * 1000, 2),
					"workflow_name": session.get("active_workflow_name"),
					"username": username,
					"error": exc.message,
				}
			)
		)
	finally:
		session.clear()

	logger.info(
		json.dumps(
			{
				"event": "quart.auth.logout.completed",
				"username": username,
				"duration_ms": round((time.perf_counter() - started) * 1000, 2),
				"tool_name": "user_logoff",
				"workflow_name": session.get("active_workflow_name"),
			}
		)
	)
	return redirect("/")
