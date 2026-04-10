from pathlib import Path

from flask import Flask, jsonify, request, render_template, abort
from DAO import MySQLDatabase # Ensure this matches your .py file name
import config

app = Flask(
    __name__,
    template_folder=str(Path(__file__).resolve().parent / "app" / "templates"),
)

runtime_config = config.get_config()
db = MySQLDatabase(
    host=runtime_config.DB_HOST,
    port=runtime_config.DB_PORT,
    user=runtime_config.DB_USER,
    password=runtime_config.DB_PASSWORD,
    dbname=runtime_config.DB_NAME,
    auth_plugin=runtime_config.DB_AUTH_PLUGIN,
)


def database_error(err: str):
    """Return a structured response for database connectivity and query failures."""
    status_code = 503 if err and "Authentication plugin" in err else 500
    return jsonify({"error": err, "error_type": "database_error"}), status_code

# --- HTML ROUTES ---

@app.route('/')
def index():
    # This points at app/templates/index.html.
    return render_template('index.html')

# --- API ROUTES (Workflows) ---

@app.route('/api/workflows', methods=['GET'])
def get_all_workflows():
    code, err, data = db.select_all_from_workflow_table()
    if code == 0:
        return jsonify(data)
    return database_error(err)

@app.route('/api/workflows/<int:id>', methods=['GET'])
def get_workflow(id):
    code, err, data = db.select_from_workflow_table(id)
    if code == 0:
        return jsonify(data)
    return jsonify({"error": err}), 404

@app.route('/api/workflows', methods=['POST'])
def create_workflow():
    if not request.json:
        abort(400)
    
    # Map the incoming JSON to your DAO arguments
    req = request.json
    code, err, new_id = db.insert_into_workflow_table(
        workflow_name=req.get('name'),
        workflow_description=req.get('description'),
        workflow_type=req.get('type'),
        workflow_subtype=req.get('subtype'),
        created_by=req.get('user')
    )
    
    if code == 0:
        return jsonify({"id": new_id, "status": "created"}), 201
    return database_error(err)

# --- API ROUTES (Roles) ---

@app.route('/api/roles', methods=['GET'])
def get_all_roles():
    code, err, data = db.select_all_from_role_table()
    if code == 0:
        return jsonify(data)
    return database_error(err)

if __name__ == "__main__":
    app.run(debug=True)