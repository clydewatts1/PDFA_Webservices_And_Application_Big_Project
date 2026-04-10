#------------------------------------------------------------------------------------------------
# File: app/routes.py
# Description: Defines Flask routes and handlers for the web application.
# Prompt: 
# Refactor the Flask routes to use a Blueprint and access the database provider from the app context. Look at dao_base.py
#------------------------------------------------------------------------------------------------

from flask import Blueprint, abort, current_app, flash, jsonify, redirect, render_template, request, url_for

from app.databases.dao_base import BaseDAO

# Using a Blueprint is the cleanest way to organize routes in a factory pattern
bp = Blueprint('main', __name__)


def _route_context(**context: object) -> str:
    """Return a compact log-friendly context string for route events."""
    details = [f"{key}={value}" for key, value in context.items() if value is not None]
    return f" ({', '.join(details)})" if details else ""


def log_route_info(action: str, **context: object) -> None:
    """Log a route lifecycle info message using the Flask app logger."""
    current_app.logger.info("Route %s%s", action, _route_context(**context))


def json_success(payload: object, action: str, status_code: int = 200):
    """Return a JSON success response and log route completion."""
    log_route_info(f"{action}:success", status=status_code)
    response = jsonify(payload)
    if status_code == 200:
        return response
    return response, status_code


def get_db_provider() -> BaseDAO:
    """Return the active DAO provider stored on the Flask application context."""
    database_provider = getattr(current_app, "db", None)
    if database_provider is None:
        current_app.logger.error("Route database provider lookup failed: provider is not configured.")
        raise RuntimeError("Database provider is not configured on the Flask app.")
    return database_provider


def get_json_payload() -> dict:
    """Return the current request JSON payload or abort with 400 when missing."""
    payload = request.get_json(silent=True)
    if not payload:
        current_app.logger.error("Route %s received an empty or invalid JSON payload.", request.path)
        abort(400)
    return payload


def json_error(err: str, status_code: int = 500, action: str = "unknown"):
    """Return a normalized JSON error response for DAO-backed API routes."""
    current_app.logger.error("Route %s DAO failure: %s", action, err)
    return jsonify({"error": err}), status_code


@bp.route('/')
def index():
    """Render the workflow management page."""
    log_route_info("index:start", path=request.path)
    log_route_info("index:success", path=request.path)
    return render_template("index.html")

@bp.route('/workflow/add', methods=['POST'])
def add_workflow():
    """Create a workflow through the active DAO provider and redirect back home."""
    name = request.form.get('name')
    desc = request.form.get('description')
    w_type = request.form.get('type')
    log_route_info("add_workflow:start", name=name, workflow_type=w_type)

    db_provider = get_db_provider()
    code, err, new_id = db_provider.insert_into_workflow_table(
        workflow_name=name,
        workflow_description=desc,
        workflow_type=w_type,
        workflow_subtype="default",
        created_by="admin"
    )
    
    if code == 0:
        log_route_info("add_workflow:success", workflow_id=new_id)
        flash(f"Successfully added workflow ID: {new_id}", "success")
    else:
        current_app.logger.error("Route add_workflow DAO failure: %s", err)
        flash(f"Failed to add workflow: {err}", "danger")
        
    return redirect(url_for('main.index'))


@bp.route('/api/workflows', methods=['GET'])
def get_all_workflows():
    """Return all workflows as JSON using the active DAO provider."""
    action = "get_all_workflows"
    log_route_info(f"{action}:start")
    db_provider = get_db_provider()
    code, err, data = db_provider.select_all_from_workflow_table()
    if code == 0:
        return json_success(data, action)
    return json_error(err, 500, action)


@bp.route('/api/workflows/<int:workflow_id>', methods=['GET'])
def get_workflow(workflow_id: int):
    """Return a single workflow as JSON by identifier."""
    action = "get_workflow"
    log_route_info(f"{action}:start", workflow_id=workflow_id)
    db_provider = get_db_provider()
    code, err, data = db_provider.select_from_workflow_table(workflow_id)
    if code == 0:
        return json_success(data, action)
    return json_error(err, 404, action)


@bp.route('/api/workflows', methods=['POST'])
def create_workflow():
    """Create a workflow from a JSON payload and return the new identifier."""
    action = "create_workflow"
    payload = get_json_payload()
    log_route_info(f"{action}:start", workflow_name=payload.get('name'), workflow_type=payload.get('type'))

    db_provider = get_db_provider()
    code, err, new_id = db_provider.insert_into_workflow_table(
        workflow_name=payload.get('name'),
        workflow_description=payload.get('description'),
        workflow_type=payload.get('type'),
        workflow_subtype=payload.get('subtype'),
        created_by=payload.get('user'),
    )
    if code == 0:
        return json_success({"id": new_id, "status": "created"}, action, 201)
    return json_error(err, 500, action)


@bp.route('/api/workflows/<int:workflow_id>', methods=['PUT'])
def update_workflow(workflow_id: int):
    """Update a workflow from a JSON payload and return its identifier."""
    action = "update_workflow"
    payload = get_json_payload()
    log_route_info(f"{action}:start", workflow_id=workflow_id, workflow_name=payload.get('name'))

    db_provider = get_db_provider()
    code, err, updated_id = db_provider.update_workflow_table(
        workflow_id=workflow_id,
        workflow_name=payload.get('name'),
        workflow_description=payload.get('description'),
        workflow_type=payload.get('type'),
        workflow_subtype=payload.get('subtype'),
        updated_by=payload.get('user'),
    )
    if code == 0:
        return json_success({"id": updated_id, "status": "updated"}, action)
    return json_error(err, 500, action)


@bp.route('/api/workflows/<int:workflow_id>', methods=['DELETE'])
def delete_workflow(workflow_id: int):
    """Delete a workflow by identifier and return a JSON status response."""
    action = "delete_workflow"
    log_route_info(f"{action}:start", workflow_id=workflow_id)
    db_provider = get_db_provider()
    code, err, _ = db_provider.delete_from_workflow_table(workflow_id)
    if code == 0:
        return json_success({"status": "deleted", "id": workflow_id}, action)
    return json_error(err, 500, action)


@bp.route('/api/roles', methods=['GET'])
def get_all_roles():
    """Return all roles as JSON using the active DAO provider."""
    action = "get_all_roles"
    log_route_info(f"{action}:start")
    db_provider = get_db_provider()
    code, err, data = db_provider.select_all_from_role_table()
    if code == 0:
        return json_success(data, action)
    return json_error(err, 500, action)


@bp.route('/api/roles/<int:role_id>', methods=['GET'])
def get_role(role_id: int):
    """Return a single role as JSON by identifier."""
    action = "get_role"
    log_route_info(f"{action}:start", role_id=role_id)
    db_provider = get_db_provider()
    code, err, data = db_provider.select_from_role_table(role_id)
    if code == 0:
        return json_success(data, action)
    return json_error(err, 404, action)


@bp.route('/api/roles', methods=['POST'])
def create_role():
    """Create a role from a JSON payload and return the new identifier."""
    action = "create_role"
    payload = get_json_payload()
    log_route_info(f"{action}:start", workspace_id=payload.get('workspace_id'), role_name=payload.get('name'))

    db_provider = get_db_provider()
    code, err, new_id = db_provider.insert_into_role_table(
        workspace_id=payload.get('workspace_id'),
        role_name=payload.get('name'),
        role_description=payload.get('description'),
        role_type=payload.get('type'),
        role_subtype=payload.get('subtype'),
        created_by=payload.get('user'),
    )
    if code == 0:
        return json_success({"id": new_id, "status": "created"}, action, 201)
    return json_error(err, 500, action)


@bp.route('/api/roles/<int:role_id>', methods=['PUT'])
def update_role(role_id: int):
    """Update a role from a JSON payload and return its identifier."""
    action = "update_role"
    payload = get_json_payload()
    log_route_info(f"{action}:start", role_id=role_id, workspace_id=payload.get('workspace_id'))

    db_provider = get_db_provider()
    code, err, updated_id = db_provider.update_role_table(
        role_id=role_id,
        workspace_id=payload.get('workspace_id'),
        role_name=payload.get('name'),
        role_description=payload.get('description'),
        role_type=payload.get('type'),
        role_subtype=payload.get('subtype'),
        updated_by=payload.get('user'),
    )
    if code == 0:
        return json_success({"id": updated_id, "status": "updated"}, action)
    return json_error(err, 500, action)


@bp.route('/api/roles/<int:role_id>', methods=['DELETE'])
def delete_role(role_id: int):
    """Delete a role by identifier and return a JSON status response."""
    action = "delete_role"
    log_route_info(f"{action}:start", role_id=role_id)
    db_provider = get_db_provider()
    code, err, _ = db_provider.delete_from_role_table(role_id)
    if code == 0:
        return json_success({"status": "deleted", "id": role_id}, action)
    return json_error(err, 500, action)


@bp.route('/api/guards', methods=['GET'])
def get_all_guards():
    """Return all guards as JSON using the active DAO provider."""
    action = "get_all_guards"
    log_route_info(f"{action}:start")
    db_provider = get_db_provider()
    code, err, data = db_provider.select_all_from_guard_table()
    if code == 0:
        return json_success(data, action)
    return json_error(err, 500, action)


@bp.route('/api/guards/<int:guard_id>', methods=['GET'])
def get_guard(guard_id: int):
    """Return a single guard as JSON by identifier."""
    action = "get_guard"
    log_route_info(f"{action}:start", guard_id=guard_id)
    db_provider = get_db_provider()
    code, err, data = db_provider.select_from_guard_table(guard_id)
    if code == 0:
        return json_success(data, action)
    return json_error(err, 404, action)


@bp.route('/api/guards', methods=['POST'])
def create_guard():
    """Create a guard from a JSON payload and return the new identifier."""
    action = "create_guard"
    payload = get_json_payload()
    log_route_info(f"{action}:start", workspace_id=payload.get('workspace_id'), guard_name=payload.get('name'))

    db_provider = get_db_provider()
    code, err, new_id = db_provider.insert_into_guard_table(
        workspace_id=payload.get('workspace_id'),
        guard_name=payload.get('name'),
        guard_description=payload.get('description'),
        guard_type=payload.get('type'),
        guard_subtype=payload.get('subtype'),
        created_by=payload.get('user'),
    )
    if code == 0:
        return json_success({"id": new_id, "status": "created"}, action, 201)
    return json_error(err, 500, action)


@bp.route('/api/guards/<int:guard_id>', methods=['PUT'])
def update_guard(guard_id: int):
    """Update a guard from a JSON payload and return its identifier."""
    action = "update_guard"
    payload = get_json_payload()
    log_route_info(f"{action}:start", guard_id=guard_id, workspace_id=payload.get('workspace_id'))

    db_provider = get_db_provider()
    code, err, updated_id = db_provider.update_guard_table(
        guard_id=guard_id,
        workspace_id=payload.get('workspace_id'),
        guard_name=payload.get('name'),
        guard_description=payload.get('description'),
        guard_type=payload.get('type'),
        guard_subtype=payload.get('subtype'),
        updated_by=payload.get('user'),
    )
    if code == 0:
        return json_success({"id": updated_id, "status": "updated"}, action)
    return json_error(err, 500, action)


@bp.route('/api/guards/<int:guard_id>', methods=['DELETE'])
def delete_guard(guard_id: int):
    """Delete a guard by identifier and return a JSON status response."""
    action = "delete_guard"
    log_route_info(f"{action}:start", guard_id=guard_id)
    db_provider = get_db_provider()
    code, err, _ = db_provider.delete_from_guard_table(guard_id)
    if code == 0:
        return json_success({"status": "deleted", "id": guard_id}, action)
    return json_error(err, 500, action)


@bp.route('/api/interactions', methods=['GET'])
def get_all_interactions():
    """Return all interactions as JSON using the active DAO provider."""
    action = "get_all_interactions"
    log_route_info(f"{action}:start")
    db_provider = get_db_provider()
    code, err, data = db_provider.select_all_from_interaction_table()
    if code == 0:
        return json_success(data, action)
    return json_error(err, 500, action)


@bp.route('/api/interactions/<int:interaction_id>', methods=['GET'])
def get_interaction(interaction_id: int):
    """Return a single interaction as JSON by identifier."""
    action = "get_interaction"
    log_route_info(f"{action}:start", interaction_id=interaction_id)
    db_provider = get_db_provider()
    code, err, data = db_provider.select_from_interaction_table(interaction_id)
    if code == 0:
        return json_success(data, action)
    return json_error(err, 404, action)


@bp.route('/api/interactions', methods=['POST'])
def create_interaction():
    """Create an interaction from a JSON payload and return the new identifier."""
    action = "create_interaction"
    payload = get_json_payload()
    log_route_info(
        f"{action}:start",
        interaction_id=payload.get('interaction_id'),
        workflow_id=payload.get('workflow_id'),
    )

    db_provider = get_db_provider()
    code, err, new_id = db_provider.insert_into_interaction_table(
        interaction_id=payload.get('interaction_id'),
        workflow_id=payload.get('workflow_id'),
        interaction_name=payload.get('name'),
        created_by=payload.get('user'),
    )
    if code == 0:
        return json_success({"id": new_id, "status": "created"}, action, 201)
    return json_error(err, 500, action)


@bp.route('/api/interactions/<int:interaction_id>', methods=['PUT'])
def update_interaction(interaction_id: int):
    """Update an interaction from a JSON payload and return its identifier."""
    action = "update_interaction"
    payload = get_json_payload()
    log_route_info(f"{action}:start", interaction_id=interaction_id, workflow_id=payload.get('workflow_id'))

    db_provider = get_db_provider()
    code, err, updated_id = db_provider.update_interaction_table(
        interaction_id=interaction_id,
        workflow_id=payload.get('workflow_id'),
        interaction_name=payload.get('name'),
        updated_by=payload.get('user'),
    )
    if code == 0:
        return json_success({"id": updated_id, "status": "updated"}, action)
    return json_error(err, 500, action)


@bp.route('/api/interactions/<int:interaction_id>', methods=['DELETE'])
def delete_interaction(interaction_id: int):
    """Delete an interaction by identifier and return a JSON status response."""
    action = "delete_interaction"
    log_route_info(f"{action}:start", interaction_id=interaction_id)
    db_provider = get_db_provider()
    code, err, _ = db_provider.delete_from_interaction_table(interaction_id)
    if code == 0:
        return json_success({"status": "deleted", "id": interaction_id}, action)
    return json_error(err, 500, action)


@bp.route('/api/interaction-components', methods=['GET'])
def get_all_interaction_components():
    """Return all interaction components as JSON using the active DAO provider."""
    action = "get_all_interaction_components"
    log_route_info(f"{action}:start")
    db_provider = get_db_provider()
    code, err, data = db_provider.select_all_from_interaction_component_table()
    if code == 0:
        return json_success(data, action)
    return json_error(err, 500, action)


@bp.route('/api/interaction-components/<int:interaction_component_id>', methods=['GET'])
def get_interaction_component(interaction_component_id: int):
    """Return a single interaction component as JSON by identifier."""
    action = "get_interaction_component"
    log_route_info(f"{action}:start", interaction_component_id=interaction_component_id)
    db_provider = get_db_provider()
    code, err, data = db_provider.select_from_interaction_component_table(interaction_component_id)
    if code == 0:
        return json_success(data, action)
    return json_error(err, 404, action)


@bp.route('/api/interaction-components', methods=['POST'])
def create_interaction_component():
    """Create an interaction component from a JSON payload and return the new identifier."""
    action = "create_interaction_component"
    payload = get_json_payload()
    log_route_info(
        f"{action}:start",
        interaction_id=payload.get('interaction_id'),
        guard_id=payload.get('guard_id'),
        role_id=payload.get('role_id'),
    )

    db_provider = get_db_provider()
    code, err, new_id = db_provider.insert_into_interaction_component_table(
        interaction_component_name=payload.get('name'),
        interaction_component_description=payload.get('description'),
        interaction_component_type=payload.get('type'),
        interaction_component_subtype=payload.get('subtype'),
        interaction_id=payload.get('interaction_id'),
        guard_id=payload.get('guard_id'),
        role_id=payload.get('role_id'),
        direction=payload.get('direction'),
        created_by=payload.get('user'),
    )
    if code == 0:
        return json_success({"id": new_id, "status": "created"}, action, 201)
    return json_error(err, 500, action)


@bp.route('/api/interaction-components/<int:interaction_component_id>', methods=['PUT'])
def update_interaction_component(interaction_component_id: int):
    """Update an interaction component from a JSON payload and return its identifier."""
    action = "update_interaction_component"
    payload = get_json_payload()
    log_route_info(
        f"{action}:start",
        interaction_component_id=interaction_component_id,
        interaction_id=payload.get('interaction_id'),
    )

    db_provider = get_db_provider()
    code, err, updated_id = db_provider.update_interaction_component_table(
        interaction_component_id=interaction_component_id,
        interaction_component_name=payload.get('name'),
        interaction_component_description=payload.get('description'),
        interaction_component_type=payload.get('type'),
        interaction_component_subtype=payload.get('subtype'),
        interaction_id=payload.get('interaction_id'),
        guard_id=payload.get('guard_id'),
        role_id=payload.get('role_id'),
        direction=payload.get('direction'),
        updated_by=payload.get('user'),
    )
    if code == 0:
        return json_success({"id": updated_id, "status": "updated"}, action)
    return json_error(err, 500, action)


@bp.route('/api/interaction-components/<int:interaction_component_id>', methods=['DELETE'])
def delete_interaction_component(interaction_component_id: int):
    """Delete an interaction component by identifier and return a JSON status response."""
    action = "delete_interaction_component"
    log_route_info(f"{action}:start", interaction_component_id=interaction_component_id)
    db_provider = get_db_provider()
    code, err, _ = db_provider.delete_from_interaction_component_table(interaction_component_id)
    if code == 0:
        return json_success({"status": "deleted", "id": interaction_component_id}, action)
    return json_error(err, 500, action)