# Roles

Roles represent people or systems that participate in the active workflow.

## Common Tasks

- Create a role from the drawer.
- Update role name, description, type, and subtype.
- Delete a role from the current workflow.

## Important Behavior

- Roles are filtered to the active workflow only.
- New roles are automatically attached to the active workflow context.
- Requests without a valid session token are rejected.
- Roles can be linked from Interaction Components.

## Tips

- Use clear names such as `Approver`, `Reviewer`, or `System Agent`.
- Use type and subtype consistently across a workflow.
- Delete unused roles to keep component options clean.
