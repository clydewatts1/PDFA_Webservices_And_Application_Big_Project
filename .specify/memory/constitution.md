# **PDFA Webservices and Application Big Project Constitution**

## **Core Principles**

### **I. Strict Three-Tier Architecture**

The system MUST be implemented as a strict three-tier chain: Database \-\> MCP Server \-\>

Flask Web Server. Responsibilities MUST stop at tier boundaries. The database tier stores

state, the MCP server owns business logic and persistence orchestration, and the Flask web

server owns HTTP views, forms, and presentation flow. Direct bypasses across tiers,

including shared persistence code or direct database access from Flask, are prohibited.

Rationale: this preserves separation of concerns, keeps the architecture reviewable, and

matches the project's required delivery model.

### **II. Standardized MCP Communication**

The Flask application MUST communicate with the MCP server exclusively via HTTP using

JSON-RPC over SSE or streamable-http contracts. In-process imports, direct Python function

calls, local ORM reuse, and any non-HTTP shortcut between Flask and MCP are prohibited.

Every cross-tier interaction MUST be expressed as a documented MCP tool or streaming

contract so the system remains testable and replaceable at the interface boundary.

Rationale: the project must demonstrate service-oriented communication rather than a

collapsed monolith.

### **II.a MCP Server Framework Mandate**

The MCP server tier MUST be implemented using the official Python mcp library (available at https://github.com/modelcontextprotocol/python-sdk),

specifically utilizing the FastMCP class. The MCP server MUST NOT be implemented

using Flask, Quart, or any other web framework to manually handle JSON-RPC, queues,

or event streams. Furthermore, the FastMCP implementation MUST be parameterized

to support running via stdio, sse, and streamable-http transports (e.g., via CLI

arguments or environment variables) to support both local debugging and web-tier

integration. Rationale: The official library natively and asynchronously handles the

complex JSON-RPC lifecycle and protocol handshakes. Rebuilding this manually in Flask

or Quart introduces severe blocking issues, incorrect event names, and unnecessary complexity.

### **III. SQLAlchemy Containment and Data Access Encapsulation**

SQLAlchemy is the only permitted library for database interaction, and it MUST reside only

inside the MCP server tier. The Flask web server MUST NOT import SQLAlchemy, execute raw

SQL, or depend on database-specific client libraries. All create, read, update, delete,

and integrity operations MUST be performed by MCP tools that encapsulate transactions,

validation, and persistence logic. Rationale: one persistence mechanism in one tier avoids

leaky abstractions and keeps the data contract enforceable.

### **III.a Temporal/SCD Type-2 Mandate**

Every persisted domain table MUST have a structurally identical \_Hist counterpart.

Every current and history table MUST include EffFromDateTime, EffToDateTime,

DeleteInd, InsertUserName, and UpdateUserName. The current table represents the

point-in-time active record where EffToDateTime remains in the future and DeleteInd

is 0, and it MUST contain only the single current version for a business key. The

matching \_Hist table MUST contain prior versions of that record using the same business,

temporal, and audit columns. The MCP server MUST own the current-state plus history

orchestration for every update: it MUST copy the pre-update primary row into \_Hist with

the correct closing timestamp, then update or replace the single current row in the

primary table within the same transaction. Rationale: symmetric schema with a single-row

current table keeps reads simple while preserving auditable SCD Type-2 history and

point-in-time correctness.

### **IV. Incremental Graph-Model Delivery**

Implementation MUST proceed in small, reviewable chunks, beginning with workflow table

maintenance before broader workflow behaviors. The persisted domain model MUST support the

seven-table schema of Workflow, Role, Interaction, Guard, InteractionComponent, UnitOfWork,

and Instance, and MUST preserve relational integrity through explicit SQLAlchemy

relationships, foreign keys, and domain constraints. Features that alter the domain model

MUST describe their impact on this schema before implementation. Rationale: incremental,

schema-aware delivery reduces rework and makes integrity failures visible early.

### **V. Traceable Academic-Quality Delivery**

Every meaningful development interaction MUST be traceable in Git commit history so the

project evolution is demonstrable to the instructor. Code MUST remain clean and PEP 8

compliant. Standard Python module-level and function-level docstrings MUST be used to

explain the purpose of custom business logic, but inline comments and commentary on

standard framework boilerplate (like Alembic migrations) are strictly prohibited to avoid

over-commenting. The final submission MUST include a comprehensive README, with

supplementary README files in each major directory explaining local architecture. All

external sources, including AI prompts, architectural input, and Spec Kit usage, MUST be

cited. Rationale: this project is evaluated on both technical correctness and the clarity

of the development process, balancing human readability with strict grading rubrics.

### **VI. Boundary-Aware Automated Testing**

Automated testing MUST respect the strict three-tier architecture. Tests for the Flask

web tier MUST isolate the UI logic by mocking or stubbing the MCP client, ensuring the

web tier is never directly connected to a database during its test suite. Conversely,

tests for the MCP server MUST validate business logic, SQLAlchemy transactions, and

tool execution using a dedicated test database, without relying on the Flask UI.

Furthermore, every domain entity MUST have explicit tests verifying Principle III.a

(Temporal/SCD Type-2 Mandate); specifically, tests MUST assert that updating a record

correctly inserts the prior state into the \_Hist table with closed timestamps and

updates the current table in a single transaction. Rationale: Boundary-aware testing

prevents tier leakage in the test suite and guarantees the complex temporal audit

requirements remain intact over time.

## **Architecture and Data Standards**

* Configuration MUST remain environment-agnostic. Database credentials, MCP server URLs,  
  Flask server URLs, secrets, and similar deployment values MUST be supplied through  
  environment variables, including a local .env workflow where appropriate.  
* The MCP server MUST own SQLAlchemy models, session handling, migrations, and relationship  
  enforcement for the seven-table workflow schema.  
* Every persisted domain entity MUST preserve symmetric current and \_Hist schemas with  
  the mandated temporal and audit columns, while keeping only the current version in the  
  primary table and prior versions in \_Hist.  
* The Flask web server MUST treat MCP responses as its system of record for data access and  
  MUST NOT mirror persistence logic locally.  
* Any feature that changes schema shape, HTTP contracts, or event streams MUST update the  
  relevant specification, implementation plan, and developer-facing documentation before it  
  is considered complete.

## **Development Workflow and Quality Gates**

* Work MUST be planned and implemented as discrete chunks with an independently reviewable  
  outcome. Initial chunking MUST start with workflow table maintenance, then expand to the  
  remaining workflow entities and interactions.  
* Each feature specification and implementation plan MUST state which layer is affected,  
  which MCP contracts are added or changed, whether schema integrity rules are impacted, and  
  which environment variables or deployment settings are required.  
* Reviews MUST reject any change that breaks current/\_Hist symmetry, omits mandated  
  temporal columns, stores closed historical versions in the primary table, or moves  
  current-state plus history orchestration outside the MCP server.  
* Reviews MUST reject any change that breaks the three-tier boundary, introduces direct  
  database access outside MCP, omits required documentation for external sources, or leaves  
  commit history too coarse to show development progress.  
* Reviews MUST reject any MCP server implementation that manually uses Flask/Quart instead  
  of the official FastMCP framework.  
* Completion criteria for any increment MUST include code quality review, README or docs  
  updates where relevant, and evidence that the resulting change remains demonstrable in  
  isolation.  
* Reviews MUST reject any pull request or implementation chunk that lacks automated  
  tests, fails to test the current/\_Hist temporal updates, or violates tier isolation  
  (e.g., testing Flask by connecting it directly to a SQLAlchemy test session).

## **Governance**

This constitution supersedes conflicting local habits, plans, and informal implementation

shortcuts. Amendments MUST be proposed through a documented specification or pull request

that explains the change, its rationale, the affected templates or guidance files, and any

required migration of existing work. Compliance MUST be reviewed at feature-spec, plan,

task, and implementation review time.

Versioning policy follows semantic versioning for governance documents: MAJOR for

backward-incompatible principle removals or redefinitions, MINOR for new principles or

materially expanded sections, and PATCH for clarifications that do not alter required

behavior. This amendment introduces a minor clarification to Principle II.a adding the official GitHub repository link, and is therefore released as version 2.2.1.

Every implementation review MUST verify that the current work respects the Database \-\> MCP

Server \-\> Flask Web Server boundary, preserves MCP-over-HTTP communication, utilizes the

official FastMCP library parameterized for multiple transports, keeps SQLAlchemy confined

to the MCP tier, maintains seven-table workflow schema integrity where relevant, preserves

current/\_Hist symmetry, keeps prior versions in \_Hist under MCP-owned transaction control,

includes boundary-aware automated tests for these temporal operations, documents environment

variables, records external-source attribution, and follows the project's docstring and README requirements.

**Version**: 2.2.1 | **Ratified**: 2026-03-12 | **Last Amended**: 2026-03-16