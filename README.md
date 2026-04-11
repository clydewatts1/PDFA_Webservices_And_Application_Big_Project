

## Development Guide

This repository ships a Flask web tier backed by the DAO layer in `app/databases/`. The current web flow is:

1. Sign in at `/login`.
2. Choose or create a workflow at `/select-workflow`.
3. Manage workflow-scoped entities in the dashboard sections for Workflows, Roles, Guards, Interactions, and Interaction Components.

The Flask app uses request-scoped DAO instances stored on `flask.g`, while session state stores authentication and the active workflow context.

### Directory Structure

```text
PDFA_Webservices_And_Application_Big_Project/
├── app.py
├── config.py
├── requirements.txt
├── run.py
├── pytest.ini
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── select_workflow.html
│   │   └── dashboard.html
│   ├── static/
│   │   └── js/
│   │       └── main.js
│   └── databases/
│       ├── dao_base.py
│       ├── dao_mysql.py
│       └── dao_sqllite.py
└── tests/
   ├── test_dao_shared.py
   ├── test_hello_world.py
   └── test_web_tier.py
```

### Initial Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/clydewatts1/PDFA_Webservices_And_Application_Big_Project.git
```

2. Create environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

   The DAO prefers `mysql-connector-python` but can fall back to `PyMySQL` if the active Python environment cannot negotiate the configured MySQL authentication plugin.

3. Configure database access before starting the Flask app:

   ```bash
   copy .env.example .env  # On PowerShell: Copy-Item .env.example .env
   ```

   `DB_AUTH_PLUGIN` can be left blank for connector auto-negotiation.
   If your MySQL 8 user uses `caching_sha2_password`, set `DB_AUTH_PLUGIN=caching_sha2_password`.

4. Start the application:

   ```bash
   python -m flask --app app run
   ```

   Or use:

   ```bash
   python run.py
   ```

For local development, prefer environment-backed credentials rather than editing `app.py`.

### Web Tier Notes

- Authentication is currently lightweight: any non-empty username and password are accepted for local development.
- CSRF protection is enabled for server-rendered form posts using a session-backed token.
- Workflow-scoped entities are filtered and validated server-side before create, update, and delete operations complete.
- The dashboard search bar is visual only in the current phase.

### Test Commands

Run the non-sandbox suite:

```bash
python -m pytest -q
```

Run only the Flask web-tier coverage:

```bash
python -m pytest tests/test_web_tier.py -q
```

## PythonAnywhere Deployment

1. Create a new web app on PythonAnywhere, choosing Flask and the appropriate Python version.
1. Upload your project files to the PythonAnywhere file system, maintaining the directory structure.
1. Set up a virtual environment on PythonAnywhere and install dependencies from `requirements.txt`.
1. Configure the WSGI file to point to your Flask app. For example, if your Flask app is in `my_flask_project/app`, you would add:

   ```python
   import sys
   path = '/home/yourusername/my_flask_project'
   if path not in sys.path:
       sys.path.insert(0, path)

   from app import create_app
   application = create_app()
   ```