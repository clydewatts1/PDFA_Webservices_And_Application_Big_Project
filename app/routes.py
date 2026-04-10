from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app

# Using a Blueprint is the cleanest way to organize routes in a factory pattern
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """
    Example: Selecting all workflows.
    Works for both MySQL and SQLite because the method names match.
    """
    # Access the DB provider via current_app
    code, err, workflows = current_app.db.select_all_from_workflow_table()
    
    if code != 0:
        flash(f"Error fetching workflows: {err}", "danger")
        workflows = []

    return render_template('index.html', workflows=workflows)

@bp.route('/workflow/add', methods=['POST'])
def add_workflow():
    name = request.form.get('name')
    desc = request.form.get('description')
    w_type = request.form.get('type')
    
    # Call the DAO method
    code, err, new_id = current_app.db.insert_into_workflow_table(
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