# PDFA_Webservices_And_Application_Big_Project
25-26: 8640 -- WEB SERVICES AND APPLICATIONS - BIG PROJECT



## Introduction

### Development Environment


### IDE
- Microsoft Visual Code 
- Google Antigravity

### LLM

- Development - Github Co pilot
- Design / Architect - Google Gemini Pro
- speckit

_Github Co _Pilot_

Using speckit and Specification Driven Development methodology the big project will be developed.

_Google Gemini_

Google gemini is used as a brainstorm tool and high level architect. 

_SpecKit_

SpecKit is a utility consisting of a number of prompts which drives the specification life cycle.

Constitution -> Project Specification -> Technical Specification -> Implementation Plan

https://github.com/github/spec-kit

__Installation__

specify init .

## Constitutional Baseline

The project is governed by the constitution in .specify/memory/constitution.md.

- Architecture is fixed to Database -> MCP Server -> Flask Web Server.
- Flask must talk to MCP exclusively over HTTP using JSON-RPC and/or SSE.
- SQLAlchemy is permitted only inside the MCP server layer.
- Delivery proceeds in small chunks, starting with workflow table maintenance.
- Development history must remain visible through meaningful Git commits.

## Documentation and Source Attribution

The final hand-up must include a comprehensive README that explains setup, architecture,
environment variables, and the staged delivery process.

All external sources used during development, including AI prompts, architectural research,
and Spec Kit usage, must be cited in project documentation so the development process is
auditable.
