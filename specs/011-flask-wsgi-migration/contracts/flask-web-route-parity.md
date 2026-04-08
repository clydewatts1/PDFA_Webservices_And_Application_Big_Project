# Contract: Flask Web-Tier Route Parity

## Purpose

Define the production route set that must exist in `flask_web` after migration from the Quart tier.

## Production Route Groups

| Route group | Expected routes | Auth required | MCP methods involved |
|---|---|---:|---|
| Health | `GET /` | No | `get_system_health` |
| Authentication | `GET /login`, `POST /login`, `POST /logout` | Mixed | `user_logon`, `user_logoff` |
| Workspace | `GET /dashboard`, `POST /dashboard`, `GET /entities` | Yes | `workflow.list` |
| Workflow CRUD | list/new/create/edit/update/delete routes in Flask | Yes | `workflow.list`, `workflow.get`, `workflow.create`, `workflow.update`, `workflow.delete` |
| Role CRUD | list/new/create/edit/update/delete routes in Flask | Yes | `role.list`, `role.get`, `role.create`, `role.update`, `role.delete` |
| Interaction CRUD | list/new/create/edit/update/delete routes in Flask | Yes | `interaction.list`, `interaction.get`, `interaction.create`, `interaction.update`, `interaction.delete` |
| Guard CRUD | list/new/create/edit/update/delete routes in Flask | Yes | `guard.list`, `guard.get`, `guard.create`, `guard.update`, `guard.delete` |
| Interaction Component CRUD | list/new/create/edit/update/delete routes in Flask | Yes | `interaction_component.list`, `interaction_component.get`, `interaction_component.create`, `interaction_component.update`, `interaction_component.delete` |

## Form Contract

- State-changing routes use Flask-WTF/WTForms-backed form handling.
- CSRF protection is enabled for production behavior and may be disabled only in test configuration.
- Validation failures re-render the same template with user-visible errors rather than bypassing form validation.

## Template Contract

- Templates live under `flask_web/src/templates/`.
- Shared layout and partials exist for base page chrome, flash messages, navigation, and form-error rendering.
- Health, authentication, workspace, and entity-management templates remain user-observable equivalents of the current production Quart flows.

## Explicitly Out of Scope

- Debug-only or experimental Quart surfaces.
- Any route that requires SSE, WebSockets, or async-only runtime behavior.