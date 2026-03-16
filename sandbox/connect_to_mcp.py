import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import asyncio
from mcp import ClientSession, McpError
from typing import List,Optional

import asyncio
from typing import Any, Dict, List, Optional
from mcp import ClientSession, McpError

async def _call_mcp_tool(session: ClientSession, tool_name: str, arguments: Dict[str, Any], timeout: int = 15):
    """Internal helper to execute MCP tools and parse results."""
    try:
        result = await asyncio.wait_for(
            session.call_tool(tool_name, arguments=arguments),
            timeout=timeout
        )
        
        # Parse the standard MCP content format
        if not result.content:
            return {"status": "success", "data": None}
            
        data = [c.text for c in result.content if c.type == 'text']
        return {"status": "success", "data": data[0] if len(data) == 1 else data}

    except Exception as e:
        return {"status": "error", "message": str(e)}

def is_field_nullable(field_schema: dict) -> bool:
    """
    Checks various JSON Schema patterns to see if a field accepts null.
    """
    # Pattern 1: type: ["string", "null"]
    field_type = field_schema.get("type")
    if isinstance(field_type, list) and "null" in field_type:
        return True
    
    # Pattern 2: anyOf: [{"type": "string"}, {"type": "null"}]
    if "anyOf" in field_schema:
        if any(item.get("type") == "null" for item in field_schema["anyOf"]):
            return True
            
    # Pattern 3: oneOf: [...]
    if "oneOf" in field_schema:
        if any(item.get("type") == "null" for item in field_schema["oneOf"]):
            return True

    return False


async def get_available_tools(session: ClientSession) -> List[dict]:
    """
    Fetches the list of tools from the MCP server and returns 
    a simplified list of dictionaries.
    """
    try:
        print("[*] Refreshing tool list...")
        # 1. Fetch the raw result from the session
        result = await session.list_tools()
        
        # 2. Extract and format the tool data
        # We return a list of dicts to make it easy for the rest of the app to use
        tool_list = []
        for tool in result.tools:
            tool_list.append({
                "name": tool.name,
                "description": tool.description,
                "arguments": list(tool.inputSchema.get("properties", {}).keys())
            })
            
        return tool_list

    except McpError as e:
        print(f"[!] MCP Protocol error while listing tools: {e}")
        return []
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        return []
    
async def workflow_create(session, name, actor, desc="", context=""):
    return await _call_mcp_tool(session, "workflow.create", {
        "WorkflowName": name, "actor": actor, 
        "WorkflowDescription": desc, "WorkflowContextDescription": context
    })

async def workflow_get(session, name):
    return await _call_mcp_tool(session, "workflow.get", {"WorkflowName": name})

async def workflow_list(session, limit=10, offset=0):
    return await _call_mcp_tool(session, "workflow.list", {"limit": limit, "offset": offset})

async def role_create(session, workflow, role_name, actor, config=None):
    return await _call_mcp_tool(session, "role.create", {
        "WorkflowName": workflow, "RoleName": role_name, 
        "actor": actor, "RoleConfiguration": config or {}
    })

async def role_delete(session, workflow, role_name, actor):
    return await _call_mcp_tool(session, "role.delete", {
        "WorkflowName": workflow, "RoleName": role_name, "actor": actor
    })

async def instance_create(session, workflow, instance_name, actor):
    return await _call_mcp_tool(session, "instance.create", {
        "WorkflowName": workflow, "InstanceName": instance_name, "actor": actor
    })

async def uow_get(session, uow_id):
    return await _call_mcp_tool(session, "unit_of_work.get", {"UnitOfWorkID": uow_id})

async def login(session, username, password):
    return await _call_mcp_tool(session, "user_logon", {"username": username, "password": password})

async def logout(session, username):
    return await _call_mcp_tool(session, "user_logoff", {"username": username})

async def system_health(session):
    return await _call_mcp_tool(session, "get_system_health", {"kwargs": {}})

async def check_system_health(session: ClientSession, timeout: int = 10):
    """
    Enhanced wrapper for 'get_system_health' with discovery validation 
    and robust error handling.
    """
    print(f"[*] Executing system health check (timeout: {timeout}s)...")
    
    try:
        # 1. Discovery Check: Ensure the tool exists before calling
        tools_resp = await session.list_tools()
        tool_exists = any(t.name == "get_system_health" for t in tools_resp.tools)
        
        if not tool_exists:
            return "[ERROR] Tool 'get_system_health' not found on this server."

        # 2. Execution: Calling the tool
        # We use an empty dict for kwargs as it's the standard way to 
        # satisfy a 'kwargs' schema variable in MCP.
        result = await asyncio.wait_for(
            session.call_tool("get_system_health", arguments={"kwargs": {}}),
            timeout=timeout
        )

        # 3. Parsing: Extracting text content
        if not result.content:
            return "[WARN] Health check returned successfully but contained no data."

        report_parts = [
            content.text for content in result.content 
            if hasattr(content, 'text') and content.type == 'text'
        ]
        
        return "\n".join(report_parts) if report_parts else "[WARN] No text content received."

    except asyncio.TimeoutError:
        return f"[ERROR] Health check timed out after {timeout} seconds."
    except McpError as e:
        return f"[ERROR] MCP Protocol error: {str(e)}"
    except Exception as e:
        # Catching unexpected errors (like network disconnects)
        return f"[ERROR] An unexpected error occurred: {str(e)}"
    
async def run_client():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "mcp_server.src.server"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            print("[*] Initializing session...")
            await session.initialize()
            
            tools = await get_available_tools(session)
            if not tools:
                print("[!] No tools available. Exiting.")
            else:
                print(f"[*] {len(tools)} tools available:")
                # Print a nice formatted list
                for i, tool in enumerate(tools, 1):
                    print(f"{i}. [{tool['name']}]")
                    if tool['description']:
                        # Indent description for better look
                        print(f"   Description: {tool['description']}")
                    print(f"   Schema: {list(tool['arguments'])}")
                    print("") # Newline for spacing


            # Authenticate
            auth = await login(session, "admin", "password123")
            print(f"[*] Authentication response: {auth}")
            # 5. Call the 'get_system_health' tool
            print(f"[*] Calling tool: get_system_health...")
            health_report = await check_system_health(session)
            print("\n=== System Health Report ===")
            print(health_report)
            print("============================")

if __name__ == "__main__":
    try:
        asyncio.run(run_client())
    except Exception as e:
        print(f"[ERROR] {e}")