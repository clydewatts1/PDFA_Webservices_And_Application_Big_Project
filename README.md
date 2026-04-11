# PDFA Webservices and Application

The Flask web tier provides a workflow dashboard for managing workflows, roles, guards, interactions, and interaction components through a DAO-backed service layer.

## Live Application

Use the deployed site at `https://clydewatts.pythonanywhere.com/`.

## Quick Start

1. Sign in at `/login`.
2. Enter a username and password.
3. Choose or create a workflow at `/select-workflow`.
4. Manage workflow-scoped entities in the dashboard.
5. Open the Help drawer in the header for context-sensitive guidance.

## Authentication Note

The sign-in form currently requires both username and password, but credentials are not yet validated against an identity provider. Any non-empty values are accepted.

## Local Development

1. Create a virtual environment and install dependencies.
2. Copy `.env.example` to `.env`.
3. Set the local SQLite configuration:

```text
DB_BACKEND=sqlite
DB_URL=sqlite:///local.db
```

4. Start the app with `python run.py`.

Relative SQLite URLs are resolved under the project root automatically, so `sqlite:///local.db` is safe to use locally and on PythonAnywhere.

## Application Flow

1. Sign in.
2. Select or create a workflow.
3. Use the dashboard sections for Workflows, Roles, Guards, Interactions, and Interaction Components.
4. Use `Swap Workflow` to change context without signing out.
5. Use `Log off` to clear the session.

## Documentation

- [MANUAL.md](MANUAL.md) - end-user guide for sign-in, workflow selection, dashboard usage, and Help drawer behavior
- [app/README.md](app/README.md) - Flask package architecture and DAO integration notes
- [app/help_content/index.md](app/help_content/index.md) - in-app help content source files

## Testing

Run the non-sandbox suite:

```bash
python -m pytest -q
```

Run only the Flask web-tier tests:

```bash
python -m pytest tests/test_web_tier.py -q
```

## PythonAnywhere

PythonAnywhere defaults to MySQL if no backend override is configured. To keep production on SQLite for now, set:

```text
DB_BACKEND=sqlite
DB_URL=sqlite:///local.db
```

If you later move back to MySQL, configure `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, and optionally `DB_AUTH_PLUGIN`.
