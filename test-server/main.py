# server.py
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("mcp-arroyave")



@mcp.tool()
def get_today_sentence() -> str:
    """Get today sentence"""
    return "Arroyave feels smart today"



@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"