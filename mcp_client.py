"""Module for interacting with MCP servers in a loop.

This module defines an MCPClient class that initializes MCP
sessions and handles user conversations until exit.
"""

import asyncio
import json
import logging
import os

from dotenv import load_dotenv
from openai import OpenAI

from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

MODEL = "o4-mini"


class MCPClient:
    """Client for interacting with MCP servers and OpenAI."""

    def __init__(self, config_path="mcp_config.json", model=MODEL):
        """Initialize MCPClient with config and model."""
        load_dotenv()
        self.config = self.load_config(config_path)
        self.model = model
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logging.error("OPENAI_API_KEY not set in .env")
            raise RuntimeError("OPENAI_API_KEY not set")
        self.llm_client = OpenAI(api_key=api_key)
        self.servers = self.config.get("mcpServers", {})
        self.server_sessions = {}
        self.server_tools = {}
        self.functions = []

    @staticmethod
    def load_config(path):
        """Load JSON config from the given path."""
        # Specify encoding to satisfy PylintW1514
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    async def initialize(self):
        """Initialize and cache tool descriptors for all MCP servers."""
        # Clear any previous sessions if re-initializing
        self.server_sessions.clear()
        self.server_tools.clear()
        self.functions.clear()

        for name, params in self.servers.items():
            srv_params = StdioServerParameters(
                command=params["command"],
                args=params.get("args", []),
                env=params.get("env", {}),
            )
            # List tools via temporary session, don't store the session itself
            try:
                async with stdio_client(srv_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        tools_res = await session.list_tools()
                        self.server_tools[name] = {
                            t.name: t for t in tools_res.tools
                        }
            except Exception as e:
                logging.error("Failed to initialize server %s: %s", name, e)
                # Store empty tools if initialization fails
                self.server_tools[name] = {}

        self.build_functions()

    def build_functions(self):
        """Build OpenAI function definitions."""
        for srv, tools in self.server_tools.items():
            for t_name, tool in tools.items():
                func_name = f"{srv}_{t_name}"
                schema = getattr(tool, "parameters", None)
                if not isinstance(schema, dict):
                    schema = {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Input for tool"
                            }
                        },
                        "required": ["query"],
                    }
                desc = getattr(tool, "description", "") or ""
                self.functions.append({
                    "name": func_name,
                    "description": desc,
                    "parameters": schema,
                })

    async def call_tool(self, server_name, tool_name, args):
        """Call a tool on the given server via a fresh session."""
        if server_name not in self.servers:
            raise ValueError(f"Server '{server_name}' not configured.")

        params = self.servers[server_name]
        srv_params = StdioServerParameters(
            command=params["command"],
            args=params.get("args", []),
            env=params.get("env", {}),
        )
        # Establish a new connection for each tool call
        async with stdio_client(srv_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                # Ensure the tool exists on this server before calling
                if tool_name not in self.server_tools.get(server_name, {}):
                    raise ValueError(
                        f"Tool '{tool_name}' not found on server '{server_name}'"
                    )
                return await session.call_tool(tool_name,
                                               arguments=args)

    async def handle_user_input(self, user_input):
        """Process user input and respond."""
        user_msg = {"role": "user", "content": user_input}
        router = self.llm_client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "Analyze the user's request and *all* available "
                               "tools (functions). Select the *most relevant* "
                               "tool based on the specific intent. If multiple "
                               "tools seem applicable, choose the one that best "
                               "fits the context"
                               "Ensure your choice is the most appropriate."
                },
                user_msg
            ],
            functions=self.functions,
            function_call="auto",
        )
        message = router.choices[0].message
        server_name = tool_name = None
        args = {}
        if hasattr(message, "function_call") and message.function_call:
            call = message.function_call
            try:
                args = json.loads(call.arguments)
            except json.JSONDecodeError:
                args = {}
            if "_" in call.name:
                server_name, tool_name = call.name.split("_", 1)
                logging.info("Selected MCP Server: %s", server_name)
                logging.info("Selected Tool: %s", tool_name)
        if not server_name or not tool_name:
            logging.info("No specific tool selected, using general LLM response.")
            resp = self.llm_client.chat.completions.create(
                model=self.model,
                messages=[user_msg],
            )
            print("Assistant:", resp.choices[0].message.content)
            return
        result = await self.call_tool(server_name, tool_name, args)
        prompt = (
            f"User asked: '{user_input}'. Tool '{tool_name}' "
            f"returned: {result}. Respond with a friendly answer."
        )
        friendly = self.llm_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": prompt}],
        )
        print("Assistant:", friendly.choices[0].message.content)

    async def run(self):
        """Run conversation loop until exit."""
        await self.initialize()
        print("Type 'exit' or 'quit' to stop.")
        while True:
            try:
                user_input = input("You: ")
            except (EOFError, KeyboardInterrupt):
                break
            if user_input.strip().lower() in ("exit", "quit"):
                break
            await self.handle_user_input(user_input)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(MCPClient().run())
