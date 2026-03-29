# Requirement Language Rules (FR-010)

## Goal

Keep requirements technology-agnostic and implementation-neutral.

## Rules

- Prefer outcome language (`must provide`, `must include`, `must allow`).
- Avoid implementation commitments in requirement statements (specific framework/package calls).
- Keep verification criteria objective and reviewer-observable.
- Keep protocol mention at behavior level (e.g., `HTTP JSON-RPC/SSE`) when required by architecture constraints.
