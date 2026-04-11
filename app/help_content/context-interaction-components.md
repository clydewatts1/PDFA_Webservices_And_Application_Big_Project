# Interaction Components

Interaction Components connect an interaction to optional roles, optional guards, and a direction.

## Common Tasks

- View existing interaction components for the active workflow.
- Delete components that are no longer part of the workflow design.
- To create new components, see the backend API documentation or database migration guides.


## Important Behavior

- This section is currently read-only in the UI. New components cannot be created through the dashboard.
- The selected interaction is required (for backend API use).
- Role and guard links are optional, but if provided they must belong to the active workflow.
- PDFA validates workflow boundaries on the server before saving changes.

## Tips

- Component creation is not available in the dashboard UI at this time.
- Use direction values consistently across the workflow.
- Keep descriptions specific when a component combines both role and guard logic.

