# MCP Agent

This project provides a starting point for building an AI assistant that leverages the Model Context Protocol (MCP) to interact with various external tools and services (MCP Servers).

(Based on the reference implementation: https://github.com/modelcontextprotocol/python-sdk)

## Overview

The core of the project is `mcp_client.py`, which implements a client that:

1.  Reads configuration from `mcp_config.json` (same structure used by Cline, Roo, Claude Desktop) to discover available MCP servers and their tools.
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
*   **Environment Variable Management:** Uses `.env` for sensitive information like API keys via `python-dotenv`.
*   **Asynchronous:** Built using `asyncio` for efficient I/O operations.

## Project Structure

*   `mcp_client.py`: The main application script.
*   `mcp_config.json`: Configuration file defining MCP servers, their commands, environment variables, and tools. **Do not commit sensitive data directly here if possible; prefer environment variables.**
*   `.env`: Stores environment variables (API keys, etc.). **This file should NOT be committed to Git.** (Ensure it's in `.gitignore`).
*   `pyproject.toml`: Defines project metadata and dependencies managed by `uv`.
*   `uv.lock`: Lock file for reproducible dependency installation with `uv`.
*   `.gitignore`: Specifies intentionally untracked files that Git should ignore.
*   `.python-version`: Specifies the required Python version (3.13).
*   `README.md`: This file.

## Setup

1.  **Prerequisites:**
    *   Python 3.13 or later.
    *   [`uv`](https://github.com/astral-sh/uv): Required for installing and managing Python dependencies defined in `pyproject.toml`.
    *   Install `uv` if you don't have it:
        *   **macOS / Linux:** `curl -LsSf https://astral.sh/uv/install.sh | sh`
        *   **Windows:** `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
    *   *(Note: Some MCP Servers might require additional tools like `npx` for Node.js-based servers. Check the specific server's documentation.)*
2.  **Clone the repository:**
    ```bash
    git clone https://github.com/julianarroyavez/mcp-client
    cd mcp-client
    ```
3.  **Install Dependencies:**
    *   This command uses `uv` to install the packages listed in `pyproject.toml`.
    ```bash
    uv sync
    ```
4.  **Create Environment File:**
    *   Copy `.env.example` to `.env`.
    *   Fill in the required environment variables, such as `OPENAI_API_KEY` and any credentials needed by your configured MCP servers.
5.  **Configure MCP Servers:**
    *   Edit `mcp_config.json` to define the MCP servers you want the agent to connect to. Specify the command to run each server, any necessary arguments (`args`), and environment variables (`env`).
    *   **Example Server Configurations:** The `mcp_config.json` might include servers like:
        *   **Brave Search:** ([Info](https://mcpservers.org/servers/modelcontextprotocol/brave-search)) Provides web search capabilities. Requires an API key ([Get Key](https://api-dashboard.search.brave.com/login)) added to your `.env` file (e.g., `BRAVE_SEARCH_API_KEY=your_key_here`).
        *   **File System Access:** Allows interaction with the local file system. Configuration typically involves defining an authorized base directory in `mcp_config.json`. When using the tool, replace any placeholder (like `.`) with the specific directory you want to authorize access to. Paths provided to the tool must be relative to this authorized base directory and use the correct format for the server's operating system (e.g., `folder/file.txt` for Linux/macOS, `folder\file.txt` for Windows).
        *   **mcp arroyave (Test Server):** This is a sample/test server. Its configuration, especially any file paths it uses or exposes, must be adjusted based on the actual location where the test server is running and the operating system of that machine.
    *   **Note:** Modify `mcp_config.json` and `.env` to add, remove, or change the MCP servers used by the agent according to your needs.

## Running the Agent

Execute the client script from your terminal:

```bash
# 1. Activate the Python environment managed by uv:
#    (The command might differ slightly based on your shell)
#    - Linux/macOS (bash/zsh): source .venv/bin/activate
#    - Windows (cmd.exe): .venv\Scripts\activate.bat
#    - Windows (PowerShell): .venv\Scripts\Activate.ps1
#
# 2. Run the client:
python mcp_client.py
```

The agent will initialize connections to the configured MCP servers, list their tools, and then prompt you for input. Type 'exit' or 'quit' to stop the agent.

## Testing the Setup

Once the agent is running and connected to your configured servers, you can test the interaction. For example, if you have a server configured that provides a "daily sentence" tool, you could try typing:

```
what is todays sentence
```

The agent should route this request to the appropriate tool on the relevant server and display the response.

## Extending the Agent

*   **Add More Tools:** Configure additional MCP servers in `mcp_config.json`. The agent will automatically discover and integrate their tools.
*   **Change LLM:** Modify the `MODEL` constant or the `model` parameter in `mcp_client.py` to use a different OpenAI model.
*   **Customize Routing:** IMPORTANT Adjust the system prompt used for tool selection in the `handle_user_input` method within `mcp_client.py`.