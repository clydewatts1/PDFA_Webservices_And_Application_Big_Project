creat a constitution for the project , it must cover the following
1. Architecture Mandates
1.1 Strict 3 tier layering Database->MCP Server -> Fask Web Server
1.2 Comunication Prototcol: The Flask app must interact with MCP server exclusingly via HTTP(JSON-RPC/SSE). 
1.3 Data Access Encapsulation: The flack frontend is forbidden from using SQLAlchemy or direct SQL. It must only call MCP tools to perform data operations
1.4 ORM Layer: SQLAlchemy is the sole library permitted for database interactions , and it must reside strictly within MCP Server

2. Development & Interaction Strategy

2.1 Granular Interactions: The project will build in "chunks" starting with worflow table maintenance.
2.2 Graph Integrity: The system must support a 7 table schema ( Workflow,node,edge,node2edge,node_type,edge_type, edge_note_type_map) whie maintaining relational integrity via SQLAlchemy relationships
2,4 Traceablity: Every interaction must reflect in github commit history to demonstrate the development process to the instructor

3. Deployment & Quality Standards
Environment-Agnostic: Database credentials and server URLs must be managed via environment variables (e.g., a .env file).

Academic Excellence: Code must be clean, PEP 8 compliant, and avoid "over-commenting." A comprehensive README.md is mandatory for the final hand-up.

Documentation: All outside sources, including AI prompts and Spec Kit usage, must be referenced.