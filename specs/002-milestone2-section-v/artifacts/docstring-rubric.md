# Docstring Review Rubric

## Scope
Apply to custom business-logic modules and non-trivial functions in:
- `mcp_server/src/`
- `flask_web/src/`

## Module-Level Rules
- A module docstring is required when the file contains business logic, orchestration, validation, or transport handling.
- Docstrings should describe purpose and boundary responsibility in the three-tier architecture.

## Function/Method-Level Rules
- A docstring is required when intent, side-effects, or contract is not obvious from the signature.
- Docstring should clarify behavior, key inputs, and output/side-effect expectations.

## Self-Evident Exceptions
- Allowed only when behavior is obvious and low-risk.
- Must be recorded in `docstring-exceptions.md` with rationale and reviewer approval marker.

## Review Outcome States
- `present`: compliant as written.
- `added`: remediated in this milestone.
- `exception`: accepted self-evident case with rationale.
- `needs-follow-up`: incomplete and blocked for final pass.
