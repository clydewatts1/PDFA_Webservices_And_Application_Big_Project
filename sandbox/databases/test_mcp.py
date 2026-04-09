# create a barebones test file for mysql database connection and queries
# npx @modelcontextprotocol/inspector python sandbox/databases/test_mcp.py
# stio npx @modelcontextprotocol/inspector .venv/Scripts/python.exe -m sandbox.databases.test_mcp
# streamable http npx @modelcontextprotocol/inspector .venv/Scripts/python.exe -m sandbox.databases.test_mcp --transport streamable-http
import sys
import os
import mcp
import logging
import argparse

from sqlalchemy import Select

import sandbox.databases.DAO as db
# npx @modelcontextprotocol/inspector .venv/Scripts/python.exe -m sandbox.databases.test_mcp                                                                                                                      
# stre
# ensure the project root is on sys.path so test_mysql can be imported directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import sandbox.databases.DAO as DAO

from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.DEBUG)
db = DAO.MySQLDatabase('localhost', 'root', 'root')
retcode, retmsg, _ = db.connect()
if retcode != 0:
    logging.error(f"Failed to connect to the database: {retmsg}")
else:
    logging.info("Connected to the database successfully")

mcp = FastMCP("PDFA MCP Server")

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
        """Add two numbers"""
        return a + b

@mcp.tool()
def insert_workflow(workflow_name: str, workflow_description: str) -> int:
    """Insert a new workflow into the workflow table."""
    retcode, retmsg, _ = db.insert_into_workflow_table(workflow_name, workflow_description, "test_user")
    if retcode != 0:
        logging.error(f"Failed to insert workflow: {retmsg}")
        return -1
    else:
        logging.info("Inserted workflow successfully")
        return 0

if __name__ == "__main__":

    arg_parse = argparse.ArgumentParser(description="Test MCP Server")
    # transport
    # --transport stdio,sse,streamable-http
    arg_parse.add_argument("--transport", type=str, default="stdio",
                            help="Transport method for MCP server (stdio, sse, streamable-http)")
    arg_parse.add_argument("--host", type=str, default="localhost",
                            help="Host for MCP server")
    arg_parse.add_argument("--port", type=int, default=8000,
                            help="Port for MCP server")
    args = arg_parse.parse_args()
    host = args.host
    port = args.port
    transport = args.transport
    logging.info(f"Starting MCP server on {host}:{port} with transport {transport}")
    
    if transport == "stdio":
        mcp.run()
       
    elif transport == "sse":
        mcp.run(transport="sse", host=host, port=port)
    elif transport == "streamable-http":
        mcp.run(transport="streamable-http", mount_path="/mcp")
    else:
        logging.error(f"Invalid transport method: {transport}")
        exit(1)
    logging.basicConfig(level=logging.DEBUG)
    # Create an MCP server
    mcp_server = FastMCP("PDFA MCP Server", "0.1.0")    

