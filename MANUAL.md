# PDFA User Manual

## Access

Live site: `https://clydewatts.pythonanywhere.com/`

For local development, run the app and open `http://localhost:5000/`.

## Sign In

1. Open the login page.
2. Enter a username.
3. Enter a password.
4. Click `Next`.

Username and password are required, but they are not yet validated against a real identity provider. Any non-empty values are accepted.

## Workflow Selection

After sign-in, you must choose a workflow before using the dashboard.

- Select an existing workflow card to enter the dashboard.
- Use the quick-create form to add a new workflow and enter it immediately.
- Use `Log off` on this page to end the session.

Each workflow acts as a context boundary for roles, guards, interactions, and interaction components.

## Dashboard

The dashboard is organized into five sections:

- `Workflows` - create, edit, delete, and review workflow records
- `Roles` - manage workflow-scoped participants
- `Guards` - manage workflow-scoped rules, policies, or checkpoints
- `Interactions` - manage numeric interaction records and names
- `Interaction Components` - connect interactions to optional roles, optional guards, and a direction

The active workflow name is shown in the header. Summary cards at the top provide quick counts for the current context.

## Help Drawer

Use the `Help` button in the dashboard header to open the right-side help drawer.

- The drawer loads help for the current dashboard section automatically.
- Help content is rendered from markdown files in `app/help_content/`.
- If a section-specific help topic is missing, PDFA falls back to the general help index.
- Opening the Help drawer closes the entity editor drawer, and opening the entity editor closes Help.

## Swap Workflow

Use `Swap Workflow` in the header to return to workflow selection without signing out. Your session stays active, but the active workflow context is cleared until you choose another workflow.

## Log Off

Use `Log off` in the header or workflow selection page to clear the session and return to the login screen.

## Local SQLite Setup

For local development, configure:

```text
DB_BACKEND=sqlite
DB_URL=sqlite:///local.db
```

Then start the app with `python run.py`.

## Current Limitations

- Credentials are required but not validated.
- The dashboard search field is visual only.
- Data is scoped to the active workflow and cannot be shared across workflows automatically.
- Help content is file-based; missing topics fall back to the general index.
