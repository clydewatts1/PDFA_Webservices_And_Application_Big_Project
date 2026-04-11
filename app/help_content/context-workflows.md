# Workflows

Workflows are the top-level records that define dashboard context in PDFA.

## Common Tasks

- Create a new workflow from the drawer.
- Edit workflow name, description, type, and subtype.
- Delete a workflow you no longer need.
- Switch to another workflow with `Swap Workflow`.

## Important Behavior

- Workflow names must be unique.
- If you delete the active workflow, PDFA clears the current context and returns you to workflow selection.
- Roles, guards, interactions, and interaction components all belong to a workflow.

## Tips

- Use descriptive workflow names so switching context stays clear.
- Keep type and subtype consistent across related workflows.
- Review dependent records before deleting a workflow.
