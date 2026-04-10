

## Development Guide

### Directory Structure

A gemini prompt was used to get this directory structure.

/my_flask_project
├── .env                # Private credentials (GIT IGNORED)
├── .env.example        # Template for others to see required keys
├── .gitignore          # Must include: .env, __pycache__, *.pyc, instance/, local.db
├── config.py           # Logic to switch between Laptop (SQLite) and PA (MySQL)
├── requirements.txt    # List of packages (including cryptography & python-dotenv)
├── run.py              # Simple entry point for local development
│
├── /app                # All your application code lives here
│   ├── __init__.py     # Contains the "App Factory" (create_app function)
│   ├── models.py       # Database schemas (SQLAlchemy or raw SQL classes)
│   ├── routes.py       # Main URL routes
│   │
│   ├── /static         # CSS, JS, Images
│   │   ├── /css
│   │   └── /js
│   │
│   └── /templates      # HTML files
│       ├── base.html
│       └── index.html
│
└── /tests              # Unit and integration tests

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
   python app.py
   ```

For local development, prefer environment-backed credentials rather than editing `app.py`.

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