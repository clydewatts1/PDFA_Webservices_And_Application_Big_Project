from __future__ import annotations

from pathlib import Path
import re
from secrets import token_urlsafe

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from markdown import markdown

from app.databases.dao_base import BaseDAO
from app.databases.dao_mysql import MySQLDatabase


bp = Blueprint("main", __name__)


class DatabaseUnavailableError(RuntimeError):
    """Raised when the configured DAO backend cannot be used for the current request."""

_PUBLIC_ENDPOINTS = {
    "main.login",
    "main.static",
}
_WORKFLOW_OPTIONAL_ENDPOINTS = {
    "main.login",
    "main.logout",
    "main.select_workflow",
    "main.create_workflow_from_selection",
    "main.set_context",
    "main.swap_workflow",
    "main.get_all_workflows",
    "main.get_workflow",
    "main.create_workflow",
    "main.update_workflow",
    "main.delete_workflow",
}
_NAV_ITEMS = [
    {"section": "workflows", "label": "Workflows", "implemented": True},
    {"section": "roles", "label": "Roles", "implemented": True},
    {"section": "guards", "label": "Guards", "implemented": True},
    {"section": "interactions", "label": "Interactions", "implemented": True},
    {"section": "interaction-components", "label": "Interaction Components", "implemented": True},
]
_INTERACTION_COMPONENT_DIRECTIONS = {
    "inbound": "Inbound",
    "outbound": "Outbound",
    "bidirectional": "Bidirectional",
}
_HELP_TOPIC_PATTERN = re.compile(r"^[a-z0-9-]+$")
_HELP_SECTION_TOPICS = {
    "workflows": "context-workflows",
    "roles": "context-roles",
    "guards": "context-guards",
    "interactions": "context-interactions",
    "interaction-components": "context-interaction-components",
}


def _route_context(**context: object) -> str:
    """Return a compact log-friendly context string for route events."""
    details = [f"{key}={value}" for key, value in context.items() if value is not None]
    return f" ({', '.join(details)})" if details else ""


def log_route_info(action: str, **context: object) -> None:
    """Log a route lifecycle info message using the Flask app logger."""
    current_app.logger.info("Route %s%s", action, _route_context(**context))


def _is_api_request() -> bool:
    """Return True when the current request targets the JSON API surface."""
    return request.path.startswith("/api/") or request.path.startswith("/help")


def _coerce_int(value, default: int | None = None) -> int | None:
    """Convert a value to int when possible, otherwise return the provided default."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_collection(code: int, data: list | None) -> list:
    """Normalize DAO list responses so empty lists do not become UI errors."""
    if code == 0 and isinstance(data, list):
        return data
    return []


def _workflow_scoped_rows(rows: list[dict], workflow_id: int) -> list[dict]:
    """Filter records that use workspace_id or workflow_id to the active workflow context."""
    scoped_rows = []
    for row in rows:
        scope_value = row.get("workspace_id", row.get("workflow_id"))
        if _coerce_int(scope_value) == workflow_id:
            scoped_rows.append(row)
    return scoped_rows


def _rows_by_id(rows: list[dict], id_key: str) -> dict[int, dict]:
    """Return a dictionary keyed by integer identifiers for quick row lookups."""
    indexed_rows = {}
    for row in rows:
        row_id = _coerce_int(row.get(id_key))
        if row_id is not None:
            indexed_rows[row_id] = row
    return indexed_rows


def _component_workflow_id(db_provider: BaseDAO, component: dict) -> int | None:
    """Resolve the workflow for an interaction component row."""
    workflow_id = _coerce_int(component.get("workflow_id"))
    if workflow_id is not None:
        return workflow_id

    interaction_id = _coerce_int(component.get("interaction_id"))
    if interaction_id is None:
        return None

    code, _, interaction = db_provider.select_from_interaction_table(interaction_id)
    if code != 0:
        return None
    return _coerce_int(interaction.get("workflow_id"))


def _enriched_interaction_components(
    db_provider: BaseDAO,
    components: list[dict],
    interactions: list[dict],
    roles: list[dict],
    guards: list[dict],
    workflow_id: int,
) -> list[dict]:
    """Return active-workflow interaction components enriched with related display names."""
    interaction_rows = _rows_by_id(interactions, "interaction_id")
    role_rows = _rows_by_id(roles, "role_id")
    guard_rows = _rows_by_id(guards, "guard_id")
    enriched_rows = []

    for component in components:
        component_workflow_id = _component_workflow_id(db_provider, component)
        if component_workflow_id != workflow_id:
            continue

        interaction_id = _coerce_int(component.get("interaction_id"))
        role_id = _coerce_int(component.get("role_id"))
        guard_id = _coerce_int(component.get("guard_id"))
        interaction = interaction_rows.get(interaction_id or -1, {})
        role = role_rows.get(role_id or -1, {})
        guard = guard_rows.get(guard_id or -1, {})

        enriched_rows.append(
            {
                **component,
                "workflow_id": component_workflow_id,
                "interaction_name": interaction.get("interaction_name") or "Unknown interaction",
                "role_name": role.get("role_name") or "",
                "guard_name": guard.get("guard_name") or "",
                "direction_label": _INTERACTION_COMPONENT_DIRECTIONS.get(
                    str(component.get("direction") or "").lower(),
                    component.get("direction") or "-",
                ),
            }
        )

    return enriched_rows


def _enriched_interaction_component(
    db_provider: BaseDAO,
    component: dict,
    workflow_id: int,
) -> dict | None:
    """Return one interaction component enriched for dashboard rendering."""
    interaction_code, _, interactions = db_provider.select_all_from_interaction_table()
    role_code, _, roles = db_provider.select_all_from_role_table()
    guard_code, _, guards = db_provider.select_all_from_guard_table()

    scoped_interactions = _workflow_scoped_rows(_safe_collection(interaction_code, interactions), workflow_id)
    scoped_roles = _workflow_scoped_rows(_safe_collection(role_code, roles), workflow_id)
    scoped_guards = _workflow_scoped_rows(_safe_collection(guard_code, guards), workflow_id)
    enriched_rows = _enriched_interaction_components(
        db_provider,
        [component],
        scoped_interactions,
        scoped_roles,
        scoped_guards,
        workflow_id,
    )
    if not enriched_rows:
        return None
    return enriched_rows[0]


def _dot_escape(value: str | None) -> str:
    """Escape a string for safe use as a Graphviz node label."""
    return str(value or "").replace("\\", "\\\\").replace('"', '\\"')


def _build_workflow_dot(
    components: list[dict],
    interactions: dict[int, str],
    guards: dict[int, str],
    roles: dict[int, str],
) -> str:
    """Build a Graphviz DOT string representing the workflow interaction-component graph."""
    lines = [
        "digraph workflow {",
        '    graph [bgcolor="#ffffff" pad="0.4" rankdir=LR]',
        '    node [fontname="Arial" fontsize=11]',
        '    edge [fontsize=9 color="#5f6368"]',
        "",
    ]

    seen_interactions: set[int] = set()
    seen_guards: set[int] = set()
    seen_roles: set[int] = set()

    for component in components:
        interaction_id = _coerce_int(component.get("interaction_id"))
        guard_id = _coerce_int(component.get("guard_id"))
        role_id = _coerce_int(component.get("role_id"))

        if interaction_id is not None and interaction_id not in seen_interactions:
            seen_interactions.add(interaction_id)
            label = _dot_escape(interactions.get(interaction_id, f"Interaction {interaction_id}"))
            lines.append(
                f'    interaction_{interaction_id} [label="{label}" shape=ellipse'
                ' style=filled fillcolor="#E8F0FE" color="#1a73e8" fontcolor="#1a73e8"]'
            )

        if guard_id is not None and guard_id not in seen_guards:
            seen_guards.add(guard_id)
            label = _dot_escape(guards.get(guard_id, f"Guard {guard_id}"))
            lines.append(
                f'    guard_{guard_id} [label="{label}" shape=diamond'
                ' style=filled fillcolor="#E6F4EA" color="#188038" fontcolor="#188038"]'
            )

        if role_id is not None and role_id not in seen_roles:
            seen_roles.add(role_id)
            label = _dot_escape(roles.get(role_id, f"Role {role_id}"))
            lines.append(
                f'    role_{role_id} [label="{label}" shape=box'
                ' style="filled,rounded" fillcolor="#FEF3E2" color="#e37400" fontcolor="#b06000"]'
            )

    lines.append("")

    for component in components:
        interaction_id = _coerce_int(component.get("interaction_id"))
        guard_id = _coerce_int(component.get("guard_id"))
        role_id = _coerce_int(component.get("role_id"))
        if interaction_id is None:
            continue
        direction = (component.get("direction") or "outbound").lower()
        if role_id is not None:
            if direction == "outbound":
                lines.append(f"    role_{role_id} -> interaction_{interaction_id}")
            elif direction == "inbound":
                lines.append(f"    interaction_{interaction_id} -> role_{role_id}")
            elif direction == "bidirectional":
                lines.append(f"    role_{role_id} -> interaction_{interaction_id}")
                lines.append(f"    interaction_{interaction_id} -> role_{role_id}")

        if guard_id is not None:
            if direction == "outbound":
                lines.append(f"    guard_{guard_id} -> interaction_{interaction_id}")
            elif direction == "inbound":
                lines.append(f"    interaction_{interaction_id} -> guard_{guard_id}")
            elif direction == "bidirectional":
                lines.append(f"    guard_{guard_id} -> interaction_{interaction_id}")
                lines.append(f"    interaction_{interaction_id} -> guard_{guard_id}")

    lines.append("}")
    return "\n".join(lines)


def _build_initials(username: str | None) -> str:
    """Return up to two initials for the current username."""
    if not username:
        return "PD"
    parts = [part[0].upper() for part in username.split() if part]
    if not parts:
        return username[:2].upper()
    return "".join(parts[:2])


def _help_root() -> Path:
    """Return the filesystem folder that stores markdown help content."""
    return Path(current_app.root_path) / "help_content"


def _help_topic_for_section(section: str | None) -> str:
    """Map a dashboard section to its default help topic."""
    if not section:
        return "index"
    return _HELP_SECTION_TOPICS.get(section, "index")


def _help_title(topic: str) -> str:
    """Return a human-friendly title for the resolved help topic."""
    if topic == "index":
        return "Help index"
    if topic.startswith("context-"):
        topic = topic.replace("context-", "", 1)
    return topic.replace("-", " ").title()


def _load_help_topic(topic: str | None) -> dict[str, object]:
    """Load markdown help content safely from disk and render it to HTML."""
    requested_topic = (topic or "index").strip().lower()
    if not requested_topic:
        requested_topic = "index"

    if not _HELP_TOPIC_PATTERN.fullmatch(requested_topic):
        raise FileNotFoundError("Invalid help topic.")

    help_root = _help_root().resolve()
    requested_path = (help_root / f"{requested_topic}.md").resolve()
    fallback_path = (help_root / "index.md").resolve()

    if help_root not in requested_path.parents and requested_path != help_root:
        raise FileNotFoundError("Invalid help topic.")

    resolved_topic = requested_topic
    fallback_used = False
    source_path = requested_path
    if not source_path.exists() or not source_path.is_file():
        source_path = fallback_path
        resolved_topic = "index"
        fallback_used = True

    if not source_path.exists() or not source_path.is_file():
        raise FileNotFoundError("Help content is not configured.")

    markdown_text = source_path.read_text(encoding="utf-8")
    rendered_html = markdown(markdown_text, extensions=["extra", "sane_lists"])
    return {
        "topic": requested_topic,
        "resolved_topic": resolved_topic,
        "title": _help_title(resolved_topic),
        "html": rendered_html,
        "fallback": fallback_used,
    }


def _csrf_token() -> str:
    """Return a stable session-backed CSRF token for form submissions."""
    token = session.get("csrf_token")
    if not token:
        token = token_urlsafe(32)
        session["csrf_token"] = token
    return token


def _require_csrf() -> bool:
    """Validate the session-backed CSRF token for mutating form and JSON requests."""
    expected = session.get("csrf_token")
    actual = request.form.get("csrf_token")
    if not actual:
        actual = request.headers.get("X-CSRF-Token") or request.headers.get("X-CSRFToken")
    if not actual:
        payload = request.get_json(silent=True) or {}
        actual = payload.get("csrf_token")

    if expected and actual and expected == actual:
        return True

    if _is_api_request():
        return False

    flash("Your session token expired. Please try again.", "error")
    return False


@bp.app_context_processor
def inject_template_helpers():
    """Expose shared template helpers and session state across the web UI."""
    return {
        "csrf_token": _csrf_token,
        "active_username": session.get("username"),
        "active_workflow_name": session.get("workflow_name"),
        "user_initials": _build_initials(session.get("username")),
    }


@bp.before_app_request
def enforce_auth_and_context():
    """Require login and workflow context before protected routes can execute."""
    endpoint = request.endpoint or ""
    if endpoint in _PUBLIC_ENDPOINTS or endpoint.startswith("static"):
        return None

    if not session.get("logged_in"):
        if _is_api_request():
            return jsonify({"error": "Authentication required."}), 401
        return redirect(url_for("main.login"))

    if not session.get("workflow_id") and endpoint not in _WORKFLOW_OPTIONAL_ENDPOINTS:
        if _is_api_request():
            return jsonify({"error": "Workflow context required."}), 428
        return redirect(url_for("main.select_workflow"))

    return None


def json_success(payload: object, action: str, status_code: int = 200):
    """Return a JSON success response and log route completion."""
    log_route_info(f"{action}:success", status=status_code)
    response = jsonify(payload)
    if status_code == 200:
        return response
    return response, status_code


def json_error(err: str, status_code: int = 500, action: str = "unknown"):
    """Return a normalized JSON error response for DAO-backed API routes."""
    current_app.logger.error("Route %s DAO failure: %s", action, err)
    return jsonify({"error": err}), status_code


def get_json_payload() -> dict:
    """Return the current request JSON payload or abort with 400 when missing."""
    payload = request.get_json(silent=True)
    if not payload:
        current_app.logger.error("Route %s received an empty or invalid JSON payload.", request.path)
        abort(400)
    return payload


def get_db_provider() -> BaseDAO:
    """Return a request-scoped DAO provider stored on Flask's g object."""
    database_provider = getattr(g, "db", None)
    if database_provider is not None:
        return database_provider

    dao_factory = current_app.extensions.get("dao_factory")
    if not dao_factory:
        current_app.logger.error("Route database provider lookup failed: dao_factory is missing.")
        raise DatabaseUnavailableError("Database provider is not configured on the Flask app.")

    dao_class = dao_factory["class"]
    dao_kwargs = dao_factory["kwargs"]
    if dao_class is MySQLDatabase:
        missing_fields = [
            key
            for key in ("host", "user", "password", "dbname")
            if not str(dao_kwargs.get(key) or "").strip()
        ]
        if missing_fields:
            raise DatabaseUnavailableError(
                "MySQL configuration is incomplete. Set DB_HOST, DB_USER, DB_PASSWORD, and DB_NAME in "
                "your PythonAnywhere environment variables or project .env file. "
                f"Missing: {', '.join(missing_fields)}."
            )

    database_provider = dao_class(**dao_kwargs)
    code, err, _ = database_provider.connect()
    if code != 0:
        current_app.logger.error("Route database connection failed: %s", err)
        raise DatabaseUnavailableError(
            "Database connection failed. Verify the PythonAnywhere MySQL host, username, password, database "
            f"name, and auth plugin settings. Details: {err}"
        )

    g.db = database_provider
    return database_provider


@bp.app_errorhandler(DatabaseUnavailableError)
def handle_database_unavailable(err: DatabaseUnavailableError):
    """Return a user-facing response when the configured database is unavailable."""
    current_app.logger.error("Database unavailable during request: %s", err)
    if _is_api_request():
        return json_error(str(err), 503, "database_unavailable")
    return render_template("database_error.html", error_message=str(err)), 503


def _current_workflow_or_none() -> dict | None:
    """Return the active workflow from session state when it still exists in storage."""
    workflow_id = _coerce_int(session.get("workflow_id"))
    if workflow_id is None:
        return None

    db_provider = get_db_provider()
    code, err, workflow = db_provider.select_from_workflow_table(workflow_id)
    if code != 0:
        current_app.logger.warning("Active workflow could not be loaded: %s", err)
        session.pop("workflow_id", None)
        session.pop("workflow_name", None)
        return None
    return workflow


def _nav_items(active_section: str) -> list[dict[str, object]]:
    """Return sidebar navigation metadata including active state and hrefs."""
    items = []
    for item in _NAV_ITEMS:
        items.append(
            {
                **item,
                "active": item["section"] == active_section,
                "href": url_for("main.dashboard_section", section=item["section"]),
            }
        )
    return items


def _dashboard_summary(db_provider: BaseDAO, workflow_id: int) -> list[dict[str, object]]:
    """Return compact dashboard metrics for the active workflow context."""
    workflow_code, _, workflows = db_provider.select_all_from_workflow_table()
    role_code, _, roles = db_provider.select_all_from_role_table()
    guard_code, _, guards = db_provider.select_all_from_guard_table()

    role_rows = _workflow_scoped_rows(_safe_collection(role_code, roles), workflow_id)
    guard_rows = _workflow_scoped_rows(_safe_collection(guard_code, guards), workflow_id)

    return [
        {"label": "All Workflows", "value": len(_safe_collection(workflow_code, workflows)), "tone": "blue"},
        {"label": "Active Roles", "value": len(role_rows), "tone": "slate"},
        {"label": "Active Guards", "value": len(guard_rows), "tone": "slate"},
    ]


def _dashboard_context(section: str) -> dict[str, object]:
    """Build the server-rendered dashboard context for the requested section."""
    db_provider = get_db_provider()
    active_workflow = _current_workflow_or_none()
    if active_workflow is None:
        return {}

    workflow_id = _coerce_int(active_workflow.get("workflow_id"), 0) or 0
    context = {
        "active_section": section,
        "active_workflow": active_workflow,
        "nav_items": _nav_items(section),
        "summary_cards": _dashboard_summary(db_provider, workflow_id),
        "workflows": [],
        "roles": [],
        "guards": [],
        "interactions": [],
        "interaction_components": [],
        "component_role_options": [],
        "component_guard_options": [],
        "component_interaction_options": [],
        "component_direction_options": list(_INTERACTION_COMPONENT_DIRECTIONS.items()),
        "help_topic": _help_topic_for_section(section),
        "drawer_section": section
        if section in {"workflows", "roles", "guards", "interactions", "interaction-components"}
        else None,
    }

    if section == "workflows":
        code, _, workflows = db_provider.select_all_from_workflow_table()
        context["workflows"] = _safe_collection(code, workflows)
        return context

    if section == "roles":
        code, _, roles = db_provider.select_all_from_role_table()
        context["roles"] = _workflow_scoped_rows(_safe_collection(code, roles), workflow_id)
        return context

    if section == "guards":
        code, _, guards = db_provider.select_all_from_guard_table()
        context["guards"] = _workflow_scoped_rows(_safe_collection(code, guards), workflow_id)
        return context

    if section == "interactions":
        code, _, interactions = db_provider.select_all_from_interaction_table()
        context["interactions"] = _workflow_scoped_rows(_safe_collection(code, interactions), workflow_id)
        return context

    if section == "interaction-components":
        interaction_code, _, interactions = db_provider.select_all_from_interaction_table()
        role_code, _, roles = db_provider.select_all_from_role_table()
        guard_code, _, guards = db_provider.select_all_from_guard_table()
        component_code, _, interaction_components = db_provider.select_all_from_interaction_component_table()

        scoped_interactions = _workflow_scoped_rows(_safe_collection(interaction_code, interactions), workflow_id)
        scoped_roles = _workflow_scoped_rows(_safe_collection(role_code, roles), workflow_id)
        scoped_guards = _workflow_scoped_rows(_safe_collection(guard_code, guards), workflow_id)
        context["component_interaction_options"] = scoped_interactions
        context["component_role_options"] = scoped_roles
        context["component_guard_options"] = scoped_guards
        context["interaction_components"] = _enriched_interaction_components(
            db_provider,
            _safe_collection(component_code, interaction_components),
            scoped_interactions,
            scoped_roles,
            scoped_guards,
            workflow_id,
        )
        return context

    return context


def _validate_role_scope(db_provider: BaseDAO, role_id: int, workflow_id: int) -> tuple[bool, dict | None]:
    """Ensure a role belongs to the active workflow before mutation."""
    code, err, role = db_provider.select_from_role_table(role_id)
    if code != 0:
        flash(err or "Role not found.", "error")
        return False, None
    if _coerce_int(role.get("workspace_id")) != workflow_id:
        flash("That role does not belong to the active workflow.", "error")
        return False, None
    return True, role


def _validate_guard_scope(db_provider: BaseDAO, guard_id: int, workflow_id: int) -> tuple[bool, dict | None]:
    """Ensure a guard belongs to the active workflow before mutation."""
    code, err, guard = db_provider.select_from_guard_table(guard_id)
    if code != 0:
        flash(err or "Guard not found.", "error")
        return False, None
    if _coerce_int(guard.get("workspace_id")) != workflow_id:
        flash("That guard does not belong to the active workflow.", "error")
        return False, None
    return True, guard


def _validate_interaction_scope(
    db_provider: BaseDAO,
    interaction_id: int,
    workflow_id: int,
) -> tuple[bool, dict | None]:
    """Ensure an interaction belongs to the active workflow before mutation."""
    code, err, interaction = db_provider.select_from_interaction_table(interaction_id)
    if code != 0:
        flash(err or "Interaction not found.", "error")
        return False, None
    if _coerce_int(interaction.get("workflow_id")) != workflow_id:
        flash("That interaction does not belong to the active workflow.", "error")
        return False, None
    return True, interaction


def _validate_component_relationship_scope(
    db_provider: BaseDAO,
    workflow_id: int,
    interaction_id: int,
    role_id: int | None,
    guard_id: int | None,
) -> tuple[bool, dict | None, dict | None, dict | None]:
    """Ensure all selected related records belong to the active workflow."""
    interaction_valid, interaction = _validate_interaction_scope(db_provider, interaction_id, workflow_id)
    if not interaction_valid:
        return False, None, None, None

    role = None
    if role_id is not None:
        role_valid, role = _validate_role_scope(db_provider, role_id, workflow_id)
        if not role_valid:
            return False, interaction, None, None

    guard = None
    if guard_id is not None:
        guard_valid, guard = _validate_guard_scope(db_provider, guard_id, workflow_id)
        if not guard_valid:
            return False, interaction, role, None

    return True, interaction, role, guard


def _validate_interaction_component_scope(
    db_provider: BaseDAO,
    interaction_component_id: int,
    workflow_id: int,
) -> tuple[bool, dict | None]:
    """Ensure an interaction component belongs to the active workflow before mutation."""
    code, err, component = db_provider.select_from_interaction_component_table(interaction_component_id)
    if code != 0:
        flash(err or "Interaction component not found.", "error")
        return False, None

    if _component_workflow_id(db_provider, component) != workflow_id:
        flash("That interaction component does not belong to the active workflow.", "error")
        return False, None
    return True, component


@bp.route("/")
def index():
    """Redirect to the appropriate entry point based on auth and workflow context."""
    log_route_info("index:start", path=request.path)
    if not session.get("logged_in"):
        return redirect(url_for("main.login"))
    if not session.get("workflow_id"):
        return redirect(url_for("main.select_workflow"))
    return redirect(url_for("main.dashboard_section", section="workflows"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Render the PDFA sign-in page and accept basic non-empty credentials."""
    if request.method == "POST":
        if not _require_csrf():
            return redirect(url_for("main.login"))

        username = (request.form.get("username") or "").strip()
        password = (request.form.get("password") or "").strip()
        if not username or not password:
            flash("Enter both username and password.", "error")
            return redirect(url_for("main.login"))

        session.clear()
        session["logged_in"] = True
        session["username"] = username
        session["csrf_token"] = token_urlsafe(32)
        flash("Signed in successfully.", "success")
        return redirect(url_for("main.select_workflow"))

    return render_template("login.html")


@bp.route("/logout")
def logout():
    """Clear the current session and return to the sign-in screen."""
    session.clear()
    flash("Signed out.", "success")
    return redirect(url_for("main.login"))


@bp.route("/select-workflow")
def select_workflow():
    """Render the workflow chooser used to establish dashboard context."""
    db_provider = get_db_provider()
    code, _, workflows = db_provider.select_all_from_workflow_table()
    return render_template("select_workflow.html", workflows=_safe_collection(code, workflows))


@bp.route("/select-workflow/create", methods=["POST"])
def create_workflow_from_selection():
    """Create a workflow before context selection and immediately activate it."""
    if not _require_csrf():
        return redirect(url_for("main.select_workflow"))

    workflow_name = (request.form.get("workflow_name") or "").strip()
    workflow_description = (request.form.get("workflow_description") or "").strip()
    workflow_type = (request.form.get("workflow_type") or "").strip()
    workflow_subtype = (request.form.get("workflow_subtype") or "Standard").strip() or "Standard"
    if not workflow_name or not workflow_type:
        flash("Workflow name and type are required.", "error")
        return redirect(url_for("main.select_workflow"))

    db_provider = get_db_provider()
    username = session.get("username", "PDFA User")
    code, err, workflow_id = db_provider.insert_into_workflow_table(
        workflow_name=workflow_name,
        workflow_description=workflow_description,
        workflow_type=workflow_type,
        workflow_subtype=workflow_subtype,
        created_by=username,
    )
    if code != 0:
        flash(err or "Unable to create workflow.", "error")
        return redirect(url_for("main.select_workflow"))

    session["workflow_id"] = workflow_id
    session["workflow_name"] = workflow_name
    flash(f"Workflow {workflow_name} created.", "success")
    return redirect(url_for("main.dashboard_section", section="workflows"))


@bp.route("/set-context", methods=["POST"])
def set_context():
    """Persist the selected workflow in session state and enter the dashboard."""
    if not _require_csrf():
        return redirect(url_for("main.select_workflow"))

    workflow_id = _coerce_int(request.form.get("workflow_id"))
    if workflow_id is None:
        flash("Choose a workflow before continuing.", "error")
        return redirect(url_for("main.select_workflow"))

    db_provider = get_db_provider()
    code, err, workflow = db_provider.select_from_workflow_table(workflow_id)
    if code != 0:
        flash(err or "Workflow not found.", "error")
        return redirect(url_for("main.select_workflow"))

    session["workflow_id"] = workflow_id
    session["workflow_name"] = workflow.get("workflow_name")
    flash(f"Active workflow set to {workflow.get('workflow_name')}.", "success")
    return redirect(url_for("main.dashboard_section", section="workflows"))


@bp.route("/swap")
def swap_workflow():
    """Clear the active workflow context and return to workflow selection."""
    session.pop("workflow_id", None)
    session.pop("workflow_name", None)
    flash("Choose a workflow to continue.", "success")
    return redirect(url_for("main.select_workflow"))


@bp.route("/dashboard")
def dashboard_redirect():
    """Normalize the dashboard root to the workflows section."""
    return redirect(url_for("main.dashboard_section", section="workflows"))


@bp.route("/dashboard/<section>")
def dashboard_section(section: str):
    """Render the dashboard section for the active workflow context."""
    allowed_sections = {item["section"] for item in _NAV_ITEMS}
    if section not in allowed_sections:
        abort(404)

    context = _dashboard_context(section)
    if not context:
        return redirect(url_for("main.select_workflow"))
    return render_template("dashboard.html", **context)


@bp.route("/help")
@bp.route("/help/<topic>")
def help_topic(topic: str = "index"):
    """Return rendered HTML for a help topic backed by markdown files on disk."""
    try:
        payload = _load_help_topic(topic)
    except FileNotFoundError as err:
        return json_error(str(err), 404, "help_topic")

    log_route_info("help_topic:success", topic=payload["resolved_topic"])
    return jsonify(payload)


@bp.route("/dashboard/workflows/save", methods=["POST"])
def save_workflow_form():
    """Create or update a workflow from the server-rendered dashboard drawer."""
    if not _require_csrf():
        return redirect(url_for("main.dashboard_section", section="workflows"))

    workflow_name = (request.form.get("workflow_name") or "").strip()
    workflow_description = (request.form.get("workflow_description") or "").strip()
    workflow_type = (request.form.get("workflow_type") or "").strip()
    workflow_subtype = (request.form.get("workflow_subtype") or "Standard").strip() or "Standard"
    workflow_id = _coerce_int(request.form.get("workflow_id"))

    if not workflow_name or not workflow_type:
        flash("Workflow name and type are required.", "error")
        return redirect(url_for("main.dashboard_section", section="workflows"))

    db_provider = get_db_provider()
    username = session.get("username", "PDFA User")
    if workflow_id is None:
        code, err, new_id = db_provider.insert_into_workflow_table(
            workflow_name=workflow_name,
            workflow_description=workflow_description,
            workflow_type=workflow_type,
            workflow_subtype=workflow_subtype,
            created_by=username,
        )
        if code != 0:
            flash(err or "Unable to create workflow.", "error")
        else:
            flash(f"Workflow #{new_id} created.", "success")
        return redirect(url_for("main.dashboard_section", section="workflows"))

    code, err, updated_id = db_provider.update_workflow_table(
        workflow_id=workflow_id,
        workflow_name=workflow_name,
        workflow_description=workflow_description,
        workflow_type=workflow_type,
        workflow_subtype=workflow_subtype,
        updated_by=username,
    )
    if code != 0:
        flash(err or "Unable to update workflow.", "error")
    else:
        if _coerce_int(session.get("workflow_id")) == workflow_id:
            session["workflow_name"] = workflow_name
        flash(f"Workflow #{updated_id} updated.", "success")
    return redirect(url_for("main.dashboard_section", section="workflows"))


@bp.route("/dashboard/workflows/<int:workflow_id>/delete", methods=["POST"])
def delete_workflow_form(workflow_id: int):
    """Delete a workflow from the dashboard and clear context when needed."""
    if not _require_csrf():
        return redirect(url_for("main.dashboard_section", section="workflows"))

    db_provider = get_db_provider()
    code, err, _ = db_provider.delete_from_workflow_table(workflow_id)
    if code != 0:
        flash(err or "Unable to delete workflow.", "error")
        return redirect(url_for("main.dashboard_section", section="workflows"))

    if _coerce_int(session.get("workflow_id")) == workflow_id:
        session.pop("workflow_id", None)
        session.pop("workflow_name", None)
        flash("Workflow deleted. Choose another workflow to continue.", "success")
        return redirect(url_for("main.select_workflow"))

    flash(f"Workflow #{workflow_id} deleted.", "success")
    return redirect(url_for("main.dashboard_section", section="workflows"))


@bp.route("/dashboard/roles/save", methods=["POST"])
def save_role_form():
    """Create or update a role within the active workflow context."""
    if not _require_csrf():
        return redirect(url_for("main.dashboard_section", section="roles"))

    workflow_id = _coerce_int(session.get("workflow_id"))
    if workflow_id is None:
        return redirect(url_for("main.select_workflow"))

    role_name = (request.form.get("role_name") or "").strip()
    role_description = (request.form.get("role_description") or "").strip()
    role_type = (request.form.get("role_type") or "").strip()
    role_subtype = (request.form.get("role_subtype") or "Standard").strip() or "Standard"
    role_id = _coerce_int(request.form.get("role_id"))

    if not role_name or not role_type:
        flash("Role name and type are required.", "error")
        return redirect(url_for("main.dashboard_section", section="roles"))

    db_provider = get_db_provider()
    username = session.get("username", "PDFA User")
    if role_id is None:
        code, err, new_id = db_provider.insert_into_role_table(
            workspace_id=workflow_id,
            role_name=role_name,
            role_description=role_description,
            role_type=role_type,
            role_subtype=role_subtype,
            created_by=username,
        )
        if code != 0:
            flash(err or "Unable to create role.", "error")
        else:
            flash(f"Role #{new_id} created.", "success")
        return redirect(url_for("main.dashboard_section", section="roles"))

    is_valid, _ = _validate_role_scope(db_provider, role_id, workflow_id)
    if not is_valid:
        return redirect(url_for("main.dashboard_section", section="roles"))

    code, err, updated_id = db_provider.update_role_table(
        role_id=role_id,
        workspace_id=workflow_id,
        role_name=role_name,
        role_description=role_description,
        role_type=role_type,
        role_subtype=role_subtype,
        updated_by=username,
    )
    if code != 0:
        flash(err or "Unable to update role.", "error")
    else:
        flash(f"Role #{updated_id} updated.", "success")
    return redirect(url_for("main.dashboard_section", section="roles"))


@bp.route("/dashboard/roles/<int:role_id>/delete", methods=["POST"])
def delete_role_form(role_id: int):
    """Delete a role within the active workflow context."""
    if not _require_csrf():
        return redirect(url_for("main.dashboard_section", section="roles"))

    workflow_id = _coerce_int(session.get("workflow_id"))
    if workflow_id is None:
        return redirect(url_for("main.select_workflow"))

    db_provider = get_db_provider()
    is_valid, _ = _validate_role_scope(db_provider, role_id, workflow_id)
    if not is_valid:
        return redirect(url_for("main.dashboard_section", section="roles"))

    code, err, _ = db_provider.delete_from_role_table(role_id)
    if code != 0:
        flash(err or "Unable to delete role.", "error")
    else:
        flash(f"Role #{role_id} deleted.", "success")
    return redirect(url_for("main.dashboard_section", section="roles"))


@bp.route("/dashboard/guards/save", methods=["POST"])
def save_guard_form():
    """Create or update a guard within the active workflow context."""
    if not _require_csrf():
        return redirect(url_for("main.dashboard_section", section="guards"))

    workflow_id = _coerce_int(session.get("workflow_id"))
    if workflow_id is None:
        return redirect(url_for("main.select_workflow"))

    guard_name = (request.form.get("guard_name") or "").strip()
    guard_description = (request.form.get("guard_description") or "").strip()
    guard_type = (request.form.get("guard_type") or "").strip()
    guard_subtype = (request.form.get("guard_subtype") or "Standard").strip() or "Standard"
    guard_id = _coerce_int(request.form.get("guard_id"))

    if not guard_name or not guard_type:
        flash("Guard name and type are required.", "error")
        return redirect(url_for("main.dashboard_section", section="guards"))

    db_provider = get_db_provider()
    username = session.get("username", "PDFA User")
    if guard_id is None:
        code, err, new_id = db_provider.insert_into_guard_table(
            workspace_id=workflow_id,
            guard_name=guard_name,
            guard_description=guard_description,
            guard_type=guard_type,
            guard_subtype=guard_subtype,
            created_by=username,
        )
        if code != 0:
            flash(err or "Unable to create guard.", "error")
        else:
            flash(f"Guard #{new_id} created.", "success")
        return redirect(url_for("main.dashboard_section", section="guards"))

    is_valid, _ = _validate_guard_scope(db_provider, guard_id, workflow_id)
    if not is_valid:
        return redirect(url_for("main.dashboard_section", section="guards"))

    code, err, updated_id = db_provider.update_guard_table(
        guard_id=guard_id,
        workspace_id=workflow_id,
        guard_name=guard_name,
        guard_description=guard_description,
        guard_type=guard_type,
        guard_subtype=guard_subtype,
        updated_by=username,
    )
    if code != 0:
        flash(err or "Unable to update guard.", "error")
    else:
        flash(f"Guard #{updated_id} updated.", "success")
    return redirect(url_for("main.dashboard_section", section="guards"))


@bp.route("/dashboard/guards/<int:guard_id>/delete", methods=["POST"])
def delete_guard_form(guard_id: int):
    """Delete a guard within the active workflow context."""
    if not _require_csrf():
        return redirect(url_for("main.dashboard_section", section="guards"))

    workflow_id = _coerce_int(session.get("workflow_id"))
    if workflow_id is None:
        return redirect(url_for("main.select_workflow"))

    db_provider = get_db_provider()
    is_valid, _ = _validate_guard_scope(db_provider, guard_id, workflow_id)
    if not is_valid:
        return redirect(url_for("main.dashboard_section", section="guards"))

    code, err, _ = db_provider.delete_from_guard_table(guard_id)
    if code != 0:
        flash(err or "Unable to delete guard.", "error")
    else:
        flash(f"Guard #{guard_id} deleted.", "success")
    return redirect(url_for("main.dashboard_section", section="guards"))


@bp.route("/dashboard/interactions/save", methods=["POST"])
def save_interaction_form():
    """Create or update an interaction within the active workflow context."""
    if not _require_csrf():
        return redirect(url_for("main.dashboard_section", section="interactions"))

    workflow_id = _coerce_int(session.get("workflow_id"))
    if workflow_id is None:
        return redirect(url_for("main.select_workflow"))

    interaction_id_original = _coerce_int(request.form.get("interaction_id_original"))
    interaction_name = (request.form.get("interaction_name") or "").strip()

    if not interaction_name:
        flash("Interaction name is required.", "error")
        return redirect(url_for("main.dashboard_section", section="interactions"))

    db_provider = get_db_provider()
    username = session.get("username", "PDFA User")
    if interaction_id_original is None:
        code, err, new_id = db_provider.insert_into_interaction_table(
            workflow_id=workflow_id,
            interaction_name=interaction_name,
            created_by=username,
        )
        if code != 0:
            flash(err or "Unable to create interaction.", "error")
        else:
            flash(f"Interaction #{new_id} created.", "success")
        return redirect(url_for("main.dashboard_section", section="interactions"))

    is_valid, _ = _validate_interaction_scope(db_provider, interaction_id_original, workflow_id)
    if not is_valid:
        return redirect(url_for("main.dashboard_section", section="interactions"))

    code, err, updated_id = db_provider.update_interaction_table(
        interaction_id=interaction_id_original,
        workflow_id=workflow_id,
        interaction_name=interaction_name,
        updated_by=username,
    )
    if code != 0:
        flash(err or "Unable to update interaction.", "error")
    else:
        flash(f"Interaction #{updated_id} updated.", "success")
    return redirect(url_for("main.dashboard_section", section="interactions"))


@bp.route("/dashboard/interactions/<int:interaction_id>/delete", methods=["POST"])
def delete_interaction_form(interaction_id: int):
    """Delete an interaction within the active workflow context."""
    if not _require_csrf():
        return redirect(url_for("main.dashboard_section", section="interactions"))

    workflow_id = _coerce_int(session.get("workflow_id"))
    if workflow_id is None:
        return redirect(url_for("main.select_workflow"))

    db_provider = get_db_provider()
    is_valid, _ = _validate_interaction_scope(db_provider, interaction_id, workflow_id)
    if not is_valid:
        return redirect(url_for("main.dashboard_section", section="interactions"))

    code, err, _ = db_provider.delete_from_interaction_table(interaction_id)
    if code != 0:
        flash(err or "Unable to delete interaction.", "error")
    else:
        flash(f"Interaction #{interaction_id} deleted.", "success")
    return redirect(url_for("main.dashboard_section", section="interactions"))


@bp.route("/dashboard/interaction-components/save", methods=["POST"])
def save_interaction_component_form():
    """Create or update an interaction component within the active workflow context."""
    if not _require_csrf():
        return redirect(url_for("main.dashboard_section", section="interaction-components"))

    workflow_id = _coerce_int(session.get("workflow_id"))
    if workflow_id is None:
        return redirect(url_for("main.select_workflow"))

    interaction_component_id = _coerce_int(request.form.get("interaction_component_id"))
    interaction_component_name = (request.form.get("interaction_component_name") or "").strip()
    interaction_component_description = (request.form.get("interaction_component_description") or "").strip()
    interaction_component_type = (request.form.get("interaction_component_type") or "").strip()
    interaction_component_subtype = (request.form.get("interaction_component_subtype") or "").strip()
    interaction_id = _coerce_int(request.form.get("interaction_id"))
    role_id = _coerce_int(request.form.get("role_id"))
    guard_id = _coerce_int(request.form.get("guard_id"))
    direction = (request.form.get("direction") or "outbound").strip().lower()

    if not interaction_component_name or not interaction_component_type or interaction_id is None:
        flash("Component name, type, and interaction are required.", "error")
        return redirect(url_for("main.dashboard_section", section="interaction-components"))

    if direction not in _INTERACTION_COMPONENT_DIRECTIONS:
        flash("Choose a valid direction for the interaction component.", "error")
        return redirect(url_for("main.dashboard_section", section="interaction-components"))

    db_provider = get_db_provider()
    relationships_valid, _, _, _ = _validate_component_relationship_scope(
        db_provider,
        workflow_id,
        interaction_id,
        role_id,
        guard_id,
    )
    if not relationships_valid:
        return redirect(url_for("main.dashboard_section", section="interaction-components"))

    username = session.get("username", "PDFA User")
    if interaction_component_id is None:
        code, err, new_id = db_provider.insert_into_interaction_component_table(
            interaction_component_name=interaction_component_name,
            interaction_component_description=interaction_component_description,
            interaction_component_type=interaction_component_type,
            interaction_component_subtype=interaction_component_subtype,
            interaction_id=interaction_id,
            guard_id=guard_id,
            role_id=role_id,
            direction=direction,
            created_by=username,
        )
        if code != 0:
            flash(err or "Unable to create interaction component.", "error")
        else:
            flash(f"Interaction component #{new_id} created.", "success")
        return redirect(url_for("main.dashboard_section", section="interaction-components"))

    is_valid, _ = _validate_interaction_component_scope(db_provider, interaction_component_id, workflow_id)
    if not is_valid:
        return redirect(url_for("main.dashboard_section", section="interaction-components"))

    code, err, updated_id = db_provider.update_interaction_component_table(
        interaction_component_id=interaction_component_id,
        interaction_component_name=interaction_component_name,
        interaction_component_description=interaction_component_description,
        interaction_component_type=interaction_component_type,
        interaction_component_subtype=interaction_component_subtype,
        interaction_id=interaction_id,
        guard_id=guard_id,
        role_id=role_id,
        direction=direction,
        updated_by=username,
    )
    if code != 0:
        flash(err or "Unable to update interaction component.", "error")
    else:
        flash(f"Interaction component #{updated_id} updated.", "success")
    return redirect(url_for("main.dashboard_section", section="interaction-components"))


@bp.route("/dashboard/interaction-components/<int:interaction_component_id>/delete", methods=["POST"])
def delete_interaction_component_form(interaction_component_id: int):
    """Delete an interaction component within the active workflow context."""
    if not _require_csrf():
        return redirect(url_for("main.dashboard_section", section="interaction-components"))

    workflow_id = _coerce_int(session.get("workflow_id"))
    if workflow_id is None:
        return redirect(url_for("main.select_workflow"))

    db_provider = get_db_provider()
    is_valid, _ = _validate_interaction_component_scope(db_provider, interaction_component_id, workflow_id)
    if not is_valid:
        return redirect(url_for("main.dashboard_section", section="interaction-components"))

    code, err, _ = db_provider.delete_from_interaction_component_table(interaction_component_id)
    if code != 0:
        flash(err or "Unable to delete interaction component.", "error")
    else:
        flash(f"Interaction component #{interaction_component_id} deleted.", "success")
    return redirect(url_for("main.dashboard_section", section="interaction-components"))


@bp.route("/api/workflows", methods=["GET"])
def get_all_workflows():
    """Return all workflows as JSON using the active DAO provider."""
    action = "get_all_workflows"
    log_route_info(f"{action}:start")
    db_provider = get_db_provider()
    code, err, data = db_provider.select_all_from_workflow_table()
    if code == 0:
        return json_success(data, action)
    return json_error(err, 500, action)


@bp.route("/api/workflows/<int:workflow_id>", methods=["GET"])
def get_workflow(workflow_id: int):
    """Return a single workflow as JSON by identifier."""
    action = "get_workflow"
    log_route_info(f"{action}:start", workflow_id=workflow_id)
    db_provider = get_db_provider()
    code, err, data = db_provider.select_from_workflow_table(workflow_id)
    if code == 0:
        return json_success(data, action)
    return json_error(err, 404, action)


@bp.route("/api/workflows/visualize", methods=["GET"])
def visualize_workflow():
    """Return a Graphviz DOT string for the active workflow's interaction-component graph."""
    action = "visualize_workflow"
    workflow = _current_workflow_or_none()
    if not workflow:
        return json_error("No active workflow.", 428, action)

    workflow_id = _coerce_int(workflow.get("workflow_id"))
    db_provider = get_db_provider()

    int_code, _, all_interactions = db_provider.select_all_from_interaction_table()
    guard_code, _, all_guards = db_provider.select_all_from_guard_table()
    role_code, _, all_roles = db_provider.select_all_from_role_table()
    comp_code, comp_err, all_components = db_provider.select_all_from_interaction_component_table()

    if comp_code != 0:
        return json_error(comp_err, 500, action)

    scoped_interactions = _workflow_scoped_rows(_safe_collection(int_code, all_interactions), workflow_id)
    scoped_interaction_ids = {r["interaction_id"] for r in scoped_interactions}
    interactions = {r["interaction_id"]: r["interaction_name"] for r in scoped_interactions}
    guards = {
        r["guard_id"]: r["guard_name"]
        for r in _workflow_scoped_rows(_safe_collection(guard_code, all_guards), workflow_id)
    }
    roles = {
        r["role_id"]: r["role_name"]
        for r in _workflow_scoped_rows(_safe_collection(role_code, all_roles), workflow_id)
    }

    components = [
        c for c in _safe_collection(comp_code, all_components)
        if _coerce_int(c.get("interaction_id")) in scoped_interaction_ids
    ]

    dot = _build_workflow_dot(components, interactions, guards, roles)
    return json_success({"dot": dot}, action)


@bp.route("/api/workflows", methods=["POST"])
def create_workflow():
    """Create a workflow from a JSON payload and return the created workflow object."""
    action = "create_workflow"
    if not _require_csrf():
        return json_error("Invalid CSRF token.", 403, action)

    payload = get_json_payload()
    log_route_info(f"{action}:start", workflow_name=payload.get("name"), workflow_type=payload.get("type"))

    db_provider = get_db_provider()
    code, err, new_id = db_provider.insert_into_workflow_table(
        workflow_name=payload.get("name"),
        workflow_description=payload.get("description"),
        workflow_type=payload.get("type"),
        workflow_subtype=payload.get("subtype"),
        created_by=session.get("username", "PDFA User"),
    )
    if code != 0:
        return json_error(err, 500, action)

    code, err, workflow = db_provider.select_from_workflow_table(new_id)
    if code == 0:
        return json_success(workflow, action, 201)
    return json_error(err, 500, action)


@bp.route("/api/workflows/<int:workflow_id>", methods=["PUT"])
def update_workflow(workflow_id: int):
    """Update a workflow from a JSON payload and return the updated workflow object."""
    action = "update_workflow"
    if not _require_csrf():
        return json_error("Invalid CSRF token.", 403, action)

    payload = get_json_payload()
    log_route_info(f"{action}:start", workflow_id=workflow_id, workflow_name=payload.get("name"))

    db_provider = get_db_provider()
    code, err, updated_id = db_provider.update_workflow_table(
        workflow_id=workflow_id,
        workflow_name=payload.get("name"),
        workflow_description=payload.get("description"),
        workflow_type=payload.get("type"),
        workflow_subtype=payload.get("subtype"),
        updated_by=session.get("username", "PDFA User"),
    )
    if code != 0:
        return json_error(err, 500, action)

    if _coerce_int(session.get("workflow_id")) == workflow_id:
        session["workflow_name"] = payload.get("name")

    code, err, workflow = db_provider.select_from_workflow_table(updated_id)
    if code == 0:
        return json_success(workflow, action)
    return json_error(err, 500, action)


@bp.route("/api/workflows/<int:workflow_id>", methods=["DELETE"])
def delete_workflow(workflow_id: int):
    """Delete a workflow by identifier and return a JSON status response."""
    action = "delete_workflow"
    log_route_info(f"{action}:start", workflow_id=workflow_id)
    db_provider = get_db_provider()
    code, err, _ = db_provider.delete_from_workflow_table(workflow_id)
    if code == 0:
        return json_success({"status": "deleted", "id": workflow_id}, action)
    return json_error(err, 500, action)


@bp.route("/api/roles", methods=["GET"])
def get_all_roles():
    """Return all roles as JSON using the active DAO provider."""
    action = "get_all_roles"
    log_route_info(f"{action}:start")
    db_provider = get_db_provider()
    code, err, data = db_provider.select_all_from_role_table()
    if code == 0:
        return json_success(data, action)
    return json_error(err, 500, action)


@bp.route("/api/roles/<int:role_id>", methods=["GET"])
def get_role(role_id: int):
    """Return a single role as JSON by identifier."""
    action = "get_role"
    log_route_info(f"{action}:start", role_id=role_id)
    db_provider = get_db_provider()
    code, err, data = db_provider.select_from_role_table(role_id)
    if code == 0:
        return json_success(data, action)
    return json_error(err, 404, action)


@bp.route("/api/roles", methods=["POST"])
def create_role():
    """Create a role from a JSON payload and return the created role object."""
    action = "create_role"
    if not _require_csrf():
        return json_error("Invalid CSRF token.", 403, action)

    payload = get_json_payload()
    workflow_id = _coerce_int(session.get("workflow_id"))
    if workflow_id is None:
        return json_error("Workflow context required.", 428, action)

    log_route_info(f"{action}:start", workspace_id=workflow_id, role_name=payload.get("name"))

    db_provider = get_db_provider()
    code, err, new_id = db_provider.insert_into_role_table(
        workspace_id=workflow_id,
        role_name=payload.get("name"),
        role_description=payload.get("description"),
        role_type=payload.get("type"),
        role_subtype=payload.get("subtype"),
        created_by=session.get("username", "PDFA User"),
    )
    if code != 0:
        return json_error(err, 500, action)

    code, err, role = db_provider.select_from_role_table(new_id)
    if code == 0:
        return json_success(role, action, 201)
    return json_error(err, 500, action)


@bp.route("/api/roles/<int:role_id>", methods=["PUT"])
def update_role(role_id: int):
    """Update a role from a JSON payload and return the updated role object."""
    action = "update_role"
    if not _require_csrf():
        return json_error("Invalid CSRF token.", 403, action)

    payload = get_json_payload()
    workflow_id = _coerce_int(session.get("workflow_id"))
    if workflow_id is None:
        return json_error("Workflow context required.", 428, action)

    log_route_info(f"{action}:start", role_id=role_id, workspace_id=workflow_id)

    db_provider = get_db_provider()
    code, err, current_role = db_provider.select_from_role_table(role_id)
    if code != 0:
        return json_error(err, 404, action)
    if _coerce_int(current_role.get("workspace_id")) != workflow_id:
        return json_error("That role does not belong to the active workflow.", 403, action)

    code, err, updated_id = db_provider.update_role_table(
        role_id=role_id,
        workspace_id=workflow_id,
        role_name=payload.get("name"),
        role_description=payload.get("description"),
        role_type=payload.get("type"),
        role_subtype=payload.get("subtype"),
        updated_by=session.get("username", "PDFA User"),
    )
    if code != 0:
        return json_error(err, 500, action)

    code, err, role = db_provider.select_from_role_table(updated_id)
    if code == 0:
        return json_success(role, action)
    return json_error(err, 500, action)


@bp.route("/api/roles/<int:role_id>", methods=["DELETE"])
def delete_role(role_id: int):
    """Delete a role by identifier and return a JSON status response."""
    action = "delete_role"
    log_route_info(f"{action}:start", role_id=role_id)
    db_provider = get_db_provider()
    code, err, _ = db_provider.delete_from_role_table(role_id)
    if code == 0:
        return json_success({"status": "deleted", "id": role_id}, action)
    return json_error(err, 500, action)


@bp.route("/api/guards", methods=["GET"])
def get_all_guards():
    """Return all guards as JSON using the active DAO provider."""
    action = "get_all_guards"
    log_route_info(f"{action}:start")
    db_provider = get_db_provider()
    code, err, data = db_provider.select_all_from_guard_table()
    if code == 0:
        return json_success(data, action)
    return json_error(err, 500, action)


@bp.route("/api/guards/<int:guard_id>", methods=["GET"])
def get_guard(guard_id: int):
    """Return a single guard as JSON by identifier."""
    action = "get_guard"
    log_route_info(f"{action}:start", guard_id=guard_id)
    db_provider = get_db_provider()
    code, err, data = db_provider.select_from_guard_table(guard_id)
    if code == 0:
        return json_success(data, action)
    return json_error(err, 404, action)


@bp.route("/api/guards", methods=["POST"])
def create_guard():
    """Create a guard from a JSON payload and return the created guard object."""
    action = "create_guard"
    if not _require_csrf():
        return json_error("Invalid CSRF token.", 403, action)

    payload = get_json_payload()
    workflow_id = _coerce_int(session.get("workflow_id"))
    if workflow_id is None:
        return json_error("Workflow context required.", 428, action)

    log_route_info(f"{action}:start", workspace_id=workflow_id, guard_name=payload.get("name"))

    db_provider = get_db_provider()
    code, err, new_id = db_provider.insert_into_guard_table(
        workspace_id=workflow_id,
        guard_name=payload.get("name"),
        guard_description=payload.get("description"),
        guard_type=payload.get("type"),
        guard_subtype=payload.get("subtype"),
        created_by=session.get("username", "PDFA User"),
    )
    if code != 0:
        return json_error(err, 500, action)

    code, err, guard = db_provider.select_from_guard_table(new_id)
    if code == 0:
        return json_success(guard, action, 201)
    return json_error(err, 500, action)


@bp.route("/api/guards/<int:guard_id>", methods=["PUT"])
def update_guard(guard_id: int):
    """Update a guard from a JSON payload and return the updated guard object."""
    action = "update_guard"
    if not _require_csrf():
        return json_error("Invalid CSRF token.", 403, action)

    payload = get_json_payload()
    workflow_id = _coerce_int(session.get("workflow_id"))
    if workflow_id is None:
        return json_error("Workflow context required.", 428, action)

    log_route_info(f"{action}:start", guard_id=guard_id, workspace_id=workflow_id)

    db_provider = get_db_provider()
    code, err, current_guard = db_provider.select_from_guard_table(guard_id)
    if code != 0:
        return json_error(err, 404, action)
    if _coerce_int(current_guard.get("workspace_id")) != workflow_id:
        return json_error("That guard does not belong to the active workflow.", 403, action)

    code, err, updated_id = db_provider.update_guard_table(
        guard_id=guard_id,
        workspace_id=workflow_id,
        guard_name=payload.get("name"),
        guard_description=payload.get("description"),
        guard_type=payload.get("type"),
        guard_subtype=payload.get("subtype"),
        updated_by=session.get("username", "PDFA User"),
    )
    if code != 0:
        return json_error(err, 500, action)

    code, err, guard = db_provider.select_from_guard_table(updated_id)
    if code == 0:
        return json_success(guard, action)
    return json_error(err, 500, action)


@bp.route("/api/guards/<int:guard_id>", methods=["DELETE"])
def delete_guard(guard_id: int):
    """Delete a guard by identifier and return a JSON status response."""
    action = "delete_guard"
    log_route_info(f"{action}:start", guard_id=guard_id)
    db_provider = get_db_provider()
    code, err, _ = db_provider.delete_from_guard_table(guard_id)
    if code == 0:
        return json_success({"status": "deleted", "id": guard_id}, action)
    return json_error(err, 500, action)


@bp.route("/api/interactions", methods=["GET"])
def get_all_interactions():
    """Return all interactions as JSON using the active DAO provider."""
    action = "get_all_interactions"
    log_route_info(f"{action}:start")
    db_provider = get_db_provider()
    code, err, data = db_provider.select_all_from_interaction_table()
    if code == 0:
        return json_success(data, action)
    return json_error(err, 500, action)


@bp.route("/api/interactions/<int:interaction_id>", methods=["GET"])
def get_interaction(interaction_id: int):
    """Return a single interaction as JSON by identifier."""
    action = "get_interaction"
    log_route_info(f"{action}:start", interaction_id=interaction_id)
    db_provider = get_db_provider()
    code, err, data = db_provider.select_from_interaction_table(interaction_id)
    if code == 0:
        return json_success(data, action)
    return json_error(err, 404, action)


@bp.route("/api/interactions", methods=["POST"])
def create_interaction():
    """Create an interaction from a JSON payload and return the created interaction object."""
    action = "create_interaction"
    if not _require_csrf():
        return json_error("Invalid CSRF token.", 403, action)

    payload = get_json_payload()
    workflow_id = _coerce_int(session.get("workflow_id"))
    if workflow_id is None:
        return json_error("Workflow context required.", 428, action)

    log_route_info(
        f"{action}:start",
        workflow_id=workflow_id,
    )

    db_provider = get_db_provider()
    code, err, new_id = db_provider.insert_into_interaction_table(
        workflow_id=workflow_id,
        interaction_name=payload.get("name"),
        created_by=session.get("username", "PDFA User"),
    )
    if code != 0:
        return json_error(err, 500, action)

    code, err, interaction = db_provider.select_from_interaction_table(new_id)
    if code == 0:
        return json_success(interaction, action, 201)
    return json_error(err, 500, action)


@bp.route("/api/interactions/<int:interaction_id>", methods=["PUT"])
def update_interaction(interaction_id: int):
    """Update an interaction from a JSON payload and return the updated interaction object."""
    action = "update_interaction"
    if not _require_csrf():
        return json_error("Invalid CSRF token.", 403, action)

    payload = get_json_payload()
    workflow_id = _coerce_int(session.get("workflow_id"))
    if workflow_id is None:
        return json_error("Workflow context required.", 428, action)

    log_route_info(f"{action}:start", interaction_id=interaction_id, workflow_id=workflow_id)

    db_provider = get_db_provider()
    code, err, current_interaction = db_provider.select_from_interaction_table(interaction_id)
    if code != 0:
        return json_error(err, 404, action)
    if _coerce_int(current_interaction.get("workflow_id")) != workflow_id:
        return json_error("That interaction does not belong to the active workflow.", 403, action)

    code, err, updated_id = db_provider.update_interaction_table(
        interaction_id=interaction_id,
        workflow_id=workflow_id,
        interaction_name=payload.get("name"),
        updated_by=session.get("username", "PDFA User"),
    )
    if code != 0:
        return json_error(err, 500, action)

    code, err, interaction = db_provider.select_from_interaction_table(updated_id)
    if code == 0:
        return json_success(interaction, action)
    return json_error(err, 500, action)


@bp.route("/api/interactions/<int:interaction_id>", methods=["DELETE"])
def delete_interaction(interaction_id: int):
    """Delete an interaction by identifier and return a JSON status response."""
    action = "delete_interaction"
    log_route_info(f"{action}:start", interaction_id=interaction_id)
    db_provider = get_db_provider()
    code, err, _ = db_provider.delete_from_interaction_table(interaction_id)
    if code == 0:
        return json_success({"status": "deleted", "id": interaction_id}, action)
    return json_error(err, 500, action)


@bp.route("/api/interaction-components", methods=["GET"])
def get_all_interaction_components():
    """Return all interaction components as JSON using the active DAO provider."""
    action = "get_all_interaction_components"
    log_route_info(f"{action}:start")
    db_provider = get_db_provider()
    code, err, data = db_provider.select_all_from_interaction_component_table()
    if code == 0:
        return json_success(data, action)
    return json_error(err, 500, action)


@bp.route("/api/interaction-components/<int:interaction_component_id>", methods=["GET"])
def get_interaction_component(interaction_component_id: int):
    """Return a single interaction component as JSON by identifier."""
    action = "get_interaction_component"
    log_route_info(f"{action}:start", interaction_component_id=interaction_component_id)
    db_provider = get_db_provider()
    code, err, data = db_provider.select_from_interaction_component_table(interaction_component_id)
    if code == 0:
        return json_success(data, action)
    return json_error(err, 404, action)


@bp.route("/api/interaction-components", methods=["POST"])
def create_interaction_component():
    """Create an interaction component from a JSON payload and return the created object."""
    action = "create_interaction_component"
    if not _require_csrf():
        return json_error("Invalid CSRF token.", 403, action)

    payload = get_json_payload()
    workflow_id = _coerce_int(session.get("workflow_id"))
    if workflow_id is None:
        return json_error("Workflow context required.", 428, action)

    interaction_component_name = (payload.get("name") or "").strip()
    interaction_component_description = (payload.get("description") or "").strip()
    interaction_component_type = (payload.get("type") or "").strip()
    interaction_component_subtype = (payload.get("subtype") or "").strip()
    interaction_id = _coerce_int(payload.get("interaction_id"))
    role_id = _coerce_int(payload.get("role_id"))
    guard_id = _coerce_int(payload.get("guard_id"))
    direction = (payload.get("direction") or "outbound").strip().lower()

    if not interaction_component_name or not interaction_component_type or interaction_id is None:
        return json_error("Component name, type, and interaction are required.", 400, action)
    if direction not in _INTERACTION_COMPONENT_DIRECTIONS:
        return json_error("Choose a valid direction for the interaction component.", 400, action)

    log_route_info(
        f"{action}:start",
        interaction_id=interaction_id,
        guard_id=guard_id,
        role_id=role_id,
    )

    db_provider = get_db_provider()
    interaction_code, interaction_err, interaction = db_provider.select_from_interaction_table(interaction_id)
    if interaction_code != 0:
        return json_error(interaction_err or "Interaction not found.", 404, action)
    if _coerce_int(interaction.get("workflow_id")) != workflow_id:
        return json_error("That interaction does not belong to the active workflow.", 403, action)

    if role_id is not None:
        role_code, role_err, role = db_provider.select_from_role_table(role_id)
        if role_code != 0:
            return json_error(role_err or "Role not found.", 404, action)
        if _coerce_int(role.get("workspace_id")) != workflow_id:
            return json_error("That role does not belong to the active workflow.", 403, action)

    if guard_id is not None:
        guard_code, guard_err, guard = db_provider.select_from_guard_table(guard_id)
        if guard_code != 0:
            return json_error(guard_err or "Guard not found.", 404, action)
        if _coerce_int(guard.get("workspace_id")) != workflow_id:
            return json_error("That guard does not belong to the active workflow.", 403, action)

    code, err, new_id = db_provider.insert_into_interaction_component_table(
        interaction_component_name=interaction_component_name,
        interaction_component_description=interaction_component_description,
        interaction_component_type=interaction_component_type,
        interaction_component_subtype=interaction_component_subtype,
        interaction_id=interaction_id,
        guard_id=guard_id,
        role_id=role_id,
        direction=direction,
        created_by=session.get("username", "PDFA User"),
    )
    if code != 0:
        return json_error(err, 500, action)

    component_id = _coerce_int(new_id)
    if component_id is None:
        return json_error("Unable to determine the created interaction component id.", 500, action)

    code, err, component = db_provider.select_from_interaction_component_table(component_id)
    if code != 0:
        return json_error(err, 500, action)

    enriched_component = _enriched_interaction_component(db_provider, component, workflow_id)
    if enriched_component is None:
        return json_error("Unable to render the created interaction component.", 500, action)
    return json_success(enriched_component, action, 201)


@bp.route("/api/interaction-components/<int:interaction_component_id>", methods=["PUT"])
def update_interaction_component(interaction_component_id: int):
    """Update an interaction component from a JSON payload and return the updated object."""
    action = "update_interaction_component"
    if not _require_csrf():
        return json_error("Invalid CSRF token.", 403, action)

    payload = get_json_payload()
    workflow_id = _coerce_int(session.get("workflow_id"))
    if workflow_id is None:
        return json_error("Workflow context required.", 428, action)

    interaction_component_name = (payload.get("name") or "").strip()
    interaction_component_description = (payload.get("description") or "").strip()
    interaction_component_type = (payload.get("type") or "").strip()
    interaction_component_subtype = (payload.get("subtype") or "").strip()
    interaction_id = _coerce_int(payload.get("interaction_id"))
    role_id = _coerce_int(payload.get("role_id"))
    guard_id = _coerce_int(payload.get("guard_id"))
    direction = (payload.get("direction") or "outbound").strip().lower()

    if not interaction_component_name or not interaction_component_type or interaction_id is None:
        return json_error("Component name, type, and interaction are required.", 400, action)
    if direction not in _INTERACTION_COMPONENT_DIRECTIONS:
        return json_error("Choose a valid direction for the interaction component.", 400, action)

    log_route_info(
        f"{action}:start",
        interaction_component_id=interaction_component_id,
        interaction_id=interaction_id,
    )

    db_provider = get_db_provider()
    component_code, component_err, current_component = db_provider.select_from_interaction_component_table(
        interaction_component_id
    )
    if component_code != 0:
        return json_error(component_err, 404, action)

    component_workflow_id = _component_workflow_id(db_provider, current_component)
    if component_workflow_id != workflow_id:
        return json_error("That interaction component does not belong to the active workflow.", 403, action)

    interaction_code, interaction_err, interaction = db_provider.select_from_interaction_table(interaction_id)
    if interaction_code != 0:
        return json_error(interaction_err or "Interaction not found.", 404, action)
    if _coerce_int(interaction.get("workflow_id")) != workflow_id:
        return json_error("That interaction does not belong to the active workflow.", 403, action)

    if role_id is not None:
        role_code, role_err, role = db_provider.select_from_role_table(role_id)
        if role_code != 0:
            return json_error(role_err or "Role not found.", 404, action)
        if _coerce_int(role.get("workspace_id")) != workflow_id:
            return json_error("That role does not belong to the active workflow.", 403, action)

    if guard_id is not None:
        guard_code, guard_err, guard = db_provider.select_from_guard_table(guard_id)
        if guard_code != 0:
            return json_error(guard_err or "Guard not found.", 404, action)
        if _coerce_int(guard.get("workspace_id")) != workflow_id:
            return json_error("That guard does not belong to the active workflow.", 403, action)

    code, err, updated_id = db_provider.update_interaction_component_table(
        interaction_component_id=interaction_component_id,
        interaction_component_name=interaction_component_name,
        interaction_component_description=interaction_component_description,
        interaction_component_type=interaction_component_type,
        interaction_component_subtype=interaction_component_subtype,
        interaction_id=interaction_id,
        guard_id=guard_id,
        role_id=role_id,
        direction=direction,
        updated_by=session.get("username", "PDFA User"),
    )
    if code != 0:
        return json_error(err, 500, action)

    component_id = _coerce_int(updated_id, interaction_component_id)
    code, err, component = db_provider.select_from_interaction_component_table(component_id)
    if code != 0:
        return json_error(err, 500, action)

    enriched_component = _enriched_interaction_component(db_provider, component, workflow_id)
    if enriched_component is None:
        return json_error("Unable to render the updated interaction component.", 500, action)
    return json_success(enriched_component, action)


@bp.route("/api/interaction-components/<int:interaction_component_id>", methods=["DELETE"])
def delete_interaction_component(interaction_component_id: int):
    """Delete an interaction component by identifier and return a JSON status response."""
    action = "delete_interaction_component"
    log_route_info(f"{action}:start", interaction_component_id=interaction_component_id)
    db_provider = get_db_provider()
    code, err, _ = db_provider.delete_from_interaction_component_table(interaction_component_id)
    if code == 0:
        return json_success({"status": "deleted", "id": interaction_component_id}, action)
    return json_error(err, 500, action)