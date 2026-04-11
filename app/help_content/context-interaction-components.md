# Interaction Components

Interaction Components connect an interaction to optional roles, optional guards, and a direction.

## Common Tasks

- Create a component for an interaction in the active workflow.
- Set type, subtype, description, and direction.
- Link the component to a role and guard when those records exist in the same workflow.
- Delete components that are no longer part of the workflow design.

## Important Behavior

- The selected interaction is required.
- Role and guard links are optional, but if provided they must belong to the active workflow.
- PDFA validates workflow boundaries on the server before saving changes.

## Tips

- Create the parent interaction first.
- Use direction values consistently across the workflow.
- Keep descriptions specific when a component combines both role and guard logic.
