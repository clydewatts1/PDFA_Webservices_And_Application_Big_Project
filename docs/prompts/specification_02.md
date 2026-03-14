# MCP Milestone


This milestone is to implement the mcp server

## Configuration

MCP Server Name :  WB-Workflow-Configuration

MCP Configuration: 
    The MCP configuration for all resouces and tools should be stored in a yaml file. This configuration should hold all required descriptions and definitions. 
    File Name: WB-Workflow-Configuration
    The database connectivity should be in the .env file ( see env.example )


## Tools

There should be the following tools

tool: get_system_health
    This will use sql alchement to get the connection status or health. 
    The tools should return , health_status , health_status_description
    - CONNECTED,DISCONNECTED,FAILED,INITIALIZING,DEAD
    health_status_error - error code if applicable
    health_status_description - a description of the status 
    health_status_error - the error infomation if the status is FAILED,DEAD

tool: user_logon
    This is a mock logon . Input is username and password
    Input: User Name , and Password
    Output: Status - SUCCESS , DENIED , ERROR
            ErrorMessage - 
    This will be a mock function . 
    Future enhancements will handle security model

tool: user_logoff
    Input: User Name
    Output: Status - SUCCESS , ERROR

### table tools

Each current table will have a set of crud tools



Generic CRUD Tool Descriptions for YAML/SpecKit

The tools must return at mimumn a status and status message , the status is 
SUCCESS , ERROR , the status_message is the error code

1. create_[table]

Description: "Creates a new [table] record in the database. You must provide all required fields. 

Generic Inputs: Required fields (e.g., name), Optional fields (e.g., description).

2. get_[table]

Description: "Retrieves a single, specific [table] record from the database. You MUST provide the exact primary key ID of the record you want to fetch. Returns the complete details of the record."

Generic Inputs: [table]_name ( primary key) (Required).

3. list_[table]s (e.g., list_workflows)

Description: "Retrieves a list of [table] records from the database. Use this to fetch multiple records at once. Supports optional pagination to limit the number of results returned."

Generic Inputs: limit (Optional integer), offset (Optional integer).

4. update_[table]

Description: "Modifies an existing [table] record in the database. You MUST provide the primary key ID of the record you want to update, along with the specific fields you want to change. Returns the successfully updated record."

Generic Inputs: [table]_name ( primary key) (Required), updates (Required dictionary of fields to change).

5. delete_[table]

Description: "Permanently removes an existing [table] record from the database. You MUST provide the exact primary key ID of the record you wish to delete. Returns a success confirmation."

Generic Inputs: [table]_name ( primary key) (Required).


Testing.
Add a test document describing instructions on configuring MCP server and database and how to test. Please include npx instructions. Include manual instruction on how to query the database and tables directly for manual verification
