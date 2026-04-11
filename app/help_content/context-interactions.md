# Interactions

Interactions define named workflow records that act as parents for Interaction Components.

## Common Tasks

- Create an interaction with a numeric ID and name.
- Update an interaction name.
- Delete an interaction from the current workflow.

## Important Behavior

- Interaction IDs are set when created and cannot be changed afterward.
- The dashboard shows only interactions from the active workflow.
- Interaction Components use these records as their parent reference.

## Tips

- Use stable numeric IDs that fit your workflow conventions.
- Keep names action-oriented and easy to scan.
- Create interactions before creating components that depend on them.
