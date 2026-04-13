# PDFA Webservices and Application - Big Project

__Project:__ Big Project for 25-26: 8640 -- WEB SERVICES AND APPLICATIONS - TYPE A    
__Author:__ Clyde Watts   
__Course:__ 25-26: 8640 -- WEB SERVICES AND APPLICATIONS  

## Overview
The Flask web tier provides a workflow configuration dashboard for managing workflows, roles, guards, interactions, and interaction components through a DAO-backed service layer.
This is to support a colour petri net-based workflow engine, which is the focus of the project. The web tier is designed to be modular and extensible, allowing for future integration with the workflow engine and other components.

## Live Application

Use the deployed site at `https://clydewatts.pythonanywhere.com/`.

## Quick Start

1. Sign in at `/login`.
2. Enter a username and password.
    1. There is no validation against an identity provider, so any non-empty values are accepted.
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
 
## Development Notes

This was developed using a phased Meta-Prompting approach. Gemini Pro was used to generate prompts for each phase, which were then executed using VS Code Copilot Labs. The prompts and their outputs were iteratively refined to achieve the final implementation. A phased approach was used. 

1. **Planning Phase**: High-level design and architecture were defined, including the project structure and key components. [Constitution](github\agents\copilot-instructions.md)
    1. This ties down the requirements so that the next subsequent phases do not deviate from the intended design.
2. **Multiple Iterations of Implementation Phase**: The application was built in stages, starting with the backend routes and DAO layer, followed by the frontend templates and JavaScript. Each iteration focused on a specific section of the application (e.g., Workflows, Roles) to ensure modular development.
3. **Testing and Refinement Phase**: After the initial implementation, testing was conducted to identify and fix bugs, improve error handling, and enhance the user experience. This phase also included the addition of logging for better debugging and monitoring.

Note: There was a initial implementation of this project which used speckit to develop a 3 tier architecture based on DAO->MCP->Quart. This was shelved because pythonanywhere does not support Quart and MCP servers. These features are now in beta.

The initial prototyping was done in `sandbox/databases`, where there is a simple web tier and a simple DAO layer for prototyping.

## Application Architecture
Framework: Flask (using the App Factory pattern in app/__init__.py).
Entry Point: run.py for local development; WSGI configuration for PythonAnywhere.
Configuration: Managed via config.py and .env.
Environment Detection: The app detects PYTHONANYWHERE_DOMAIN to switch between Production (MySQL) and Development (SQLite).


## Databases

The application supports both MySQL (for production on PythonAnywhere) and SQLite (for local development). The DAO pattern is used to abstract away the database interactions, allowing for easy switching between the two backends based on environment detection.

### Table Schemas
The database contains the following tables:
- `workflows`: id (PK), name, description
- `roles`: id (PK), workflow_id (FK), name, description
- `guards`: id (PK), workflow_id (FK), name, description
- `interactions`: id (PK), workflow_id (FK), name, description
- `interaction_components`: id (PK), interaction_id (FK), name, description

### Workflow Table
The `workflows` table is the central entity in the application, with other tables referencing it through foreign keys. Each workflow can have multiple roles, guards, interactions, and interaction components associated with it.
Workflow is coloured petri net-based graph with nodes and edges. Nodes are interactions, edges are guards. Roles are assigned to interactions. Interaction components are assigned to interactions as well.

### Roles Table
The `roles` table contains information about the different roles that can be assigned within a workflow. Each role is linked to a specific workflow through the `workflow_id` foreign key.
A role can be either a AI Agent , Human , or Deterministic Role. This is determined by the `type` field in the `roles` table, which can have values such as 'AI Agent', 'Human', or 'Deterministic'.
A role is the only node that can modify the UOW payload. Guards only validate the UOW and move it to the next interaction, but they do not modify the payload. Interactions are just "buffers" for the UOW and do not have any intelligence or decision-making capabilities. The logic for modifying the UOW based on the role type would be implemented in the workflow engine, which is outside the scope of this web tier.

### Guards Table
The `guards` table contains information about the guards that can be applied to interactions within a workflow. A Guard is a Node which moves UOW from between interactions. Guard validates UOW state to true and moves the UOW to the next interaction. Guards are linked to workflows through the `workflow_id` foreign key.

### Interactions Table
The `interactions` table contains information about the interactions that occur within a workflow. A interaction is a Node which acts as a "buffer" for the UOW. There is no intelligence in interactions. Interactions are linked to workflows through the `workflow_id` foreign key.

### Interaction Components Table
The `interaction_components` table contains information about the components that make up an interaction. Each component is linked to a specific interaction through the `interaction_id` foreign key.

## Development Tools
- Python 3.10+
- Flask
- PyMySQL (for MySQL connectivity)
- SQLite3 (for SQLite connectivity)
- pytest (for testing)
- pythonanywhere (for deployment)
- Gemini Pro (for prompt generation)
- VS Code Copilot Labs (for executing prompts and generating code)

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


