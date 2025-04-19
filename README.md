# MCP Agent

This project provides a starting point for building an AI assistant that leverages the Model Context Protocol (MCP) to interact with various external tools and services (MCP Servers).

## Overview

The core of the project is `mcp_client.py`, which implements a client that:

1.  Reads configuration from `mcp_config.json` same structure used by Cline, Roo, Claude Desktop  to discover available MCP servers and their tools.
2.  Loads API keys and other secrets from a `.env` file.
3.  Uses an OpenAI model (configurable, defaults) to understand user input.
4.  Routes the user's request to the most appropriate tool provided by the configured MCP servers.
5.  Calls the selected tool on the relevant MCP server.
6.  Formats the tool's response using the OpenAI model for a user-friendly interaction.
7.  Runs in a loop, handling user conversation until explicitly exited.

## Features

*   **MCP Integration:** Connects to multiple MCP servers defined in `mcp_config.json`.
*   **Tool Routing:** Uses an LLM (OpenAI) to intelligently select the best tool for a user's request based on tool descriptions.
*   **Dynamic Tool Discovery:** Initializes by querying servers for available tools.
*   **Configuration Driven:** Server details, commands, and environment variables are managed in `mcp_config.json`.
*   **Environment Variable Management:** Uses `.env` for sensitive information like API keys and database credentials via `python-dotenv`.
*   **Asynchronous:** Built using `asyncio` for efficient I/O operations.

## Project Structure

*   `mcp_client.py`: The main application script.
*   `mcp_config.json`: Configuration file defining MCP servers, their commands, environment variables, and tools. **Do not commit sensitive data directly here if possible; prefer environment variables.**
*   `.env`: Stores environment variables (API keys, database URLs). **This file should NOT be committed to Git.** (Ensure it's in `.gitignore`).
*   `pyproject.toml`: Defines project metadata and dependencies managed by `uv`.
*   `uv.lock`: Lock file for reproducible dependency installation with `uv`.
*   `.gitignore`: Specifies intentionally untracked files that Git should ignore.
*   `.python-version`: Specifies the required Python version (3.13).
*   `README.md`: This file.

## Setup

1.  **Prerequisites:**
    *   Python 3.13 or later.
    *   `uv` (Python package installer/resolver).
2.  **Clone the repository (if applicable):**
    ```bash
    git clone <repository-url>
    cd mcp-agent
    ```
3.  **Install Dependencies:**
    ```bash
    uv sync
    ```
4.  **Create Environment File:**
    *   Copy `.env.example` to `.env` (if an example file exists) or create `.env` manually.
    *   Fill in the required environment variables, such as `OPENAI_API_KEY` and any credentials needed by your configured MCP servers (e.g., database URLs, other API keys).
5.  **Configure MCP Servers:**
    *   Edit `mcp_config.json` to define the MCP servers you want the agent to connect to. Specify the command to run each server, any necessary arguments (`args`), and environment variables (`env`).

## Running the Agent

Execute the client script from your terminal:

```bash
python mcp_client.py
```

The agent will initialize connections to the configured MCP servers, list their tools, and then prompt you for input. Type 'exit' or 'quit' to stop the agent.

## Extending the Agent

*   **Add More Tools:** Configure additional MCP servers in `mcp_config.json`. The agent will automatically discover and integrate their tools.
*   **Change LLM:** Modify the `MODEL` constant or the `model` parameter in `mcp_client.py` to use a different OpenAI model.
*   **Customize Routing:** IMPORTANT Adjust the system prompt used for tool selection in the `handle_user_input` method within `mcp_client.py`.