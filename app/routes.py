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


def get_db_provider() -> BaseDAO:
    """Return the active DAO provider stored on the Flask application context."""
    database_provider = getattr(current_app, "db", None)
    if database_provider is None:
        raise RuntimeError("Database provider is not configured on the Flask app.")
    return database_provider


@bp.route('/')
def index():
    """Render the workflow management page."""
    return render_template('index.html')

@bp.route('/workflow/add', methods=['POST'])
def add_workflow():
    """Create a workflow through the active DAO provider and redirect back home."""
    name = request.form.get('name')
    desc = request.form.get('description')
    w_type = request.form.get('type')

    db_provider = get_db_provider()
    code, err, new_id = db_provider.insert_into_workflow_table(
        workflow_name=name,
        workflow_description=desc,
        workflow_type=w_type,
        workflow_subtype="default",
        created_by="admin"
    )
    
    if code == 0:
        flash(f"Successfully added workflow ID: {new_id}", "success")
    else:
        flash(f"Failed to add workflow: {err}", "danger")
        
    return redirect(url_for('main.index'))


@bp.route('/api/workflows', methods=['GET'])
def get_all_workflows():
    """Return all workflows as JSON using the active DAO provider."""
    db_provider = get_db_provider()
    code, err, data = db_provider.select_all_from_workflow_table()
    if code == 0:
        return jsonify(data)
    return jsonify({"error": err}), 500


@bp.route('/api/workflows/<int:workflow_id>', methods=['GET'])
def get_workflow(workflow_id: int):
    """Return a single workflow as JSON by identifier."""
    db_provider = get_db_provider()
    code, err, data = db_provider.select_from_workflow_table(workflow_id)
    if code == 0:
        return jsonify(data)
    return jsonify({"error": err}), 404


@bp.route('/api/workflows', methods=['POST'])
def create_workflow():
    """Create a workflow from a JSON payload and return the new identifier."""
    payload = request.get_json(silent=True)
    if not payload:
        abort(400)

    db_provider = get_db_provider()
    code, err, new_id = db_provider.insert_into_workflow_table(
        workflow_name=payload.get('name'),
        workflow_description=payload.get('description'),
        workflow_type=payload.get('type'),
        workflow_subtype=payload.get('subtype'),
        created_by=payload.get('user'),
    )
    if code == 0:
        return jsonify({"id": new_id, "status": "created"}), 201
    return jsonify({"error": err}), 500


@bp.route('/api/workflows/<int:workflow_id>', methods=['DELETE'])
def delete_workflow(workflow_id: int):
    """Delete a workflow by identifier and return a JSON status response."""
    db_provider = get_db_provider()
    code, err, _ = db_provider.delete_from_workflow_table(workflow_id)
    if code == 0:
        return jsonify({"status": "deleted", "id": workflow_id})
    return jsonify({"error": err}), 500