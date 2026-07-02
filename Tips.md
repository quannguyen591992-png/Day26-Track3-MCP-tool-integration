# MCP Client Tips

These examples are meant to reduce setup friction for students. Replace `/ABSOLUTE/PATH/...` with the real path on the machine.

## Claude Code

Anthropic’s current MCP docs are here:

- https://code.claude.com/docs/en/mcp

Example `.mcp.json`:

```json
{
  "mcpServers": {
    "sqlite-lab": {
      "type": "stdio",
      "command": "python",
      "args": ["/ABSOLUTE/PATH/TO/implementation/mcp_server.py"],
      "env": {}
    }
  }
}
```

Tips:

- Use absolute paths to avoid `spawn ... ENOENT` issues.
- Claude Code supports `@sqlite-lab:schema://database`.
- If outputs are large, check `MAX_MCP_OUTPUT_TOKENS`.

## Codex

OpenAI’s current MCP doc page for Codex is here:

- https://developers.openai.com/learn/docs-mcp

Example `~/.codex/config.toml`:

```toml
[mcp_servers.sqlite_lab]
command = "python"
args = ["/ABSOLUTE/PATH/TO/implementation/mcp_server.py"]
```

Tips:

- Keep the server name short and descriptive.
- Add project instructions in `AGENTS.md` telling the agent when to use the database MCP server.
- Verify with `codex mcp list` if the CLI version supports it.

Suggested `AGENTS.md` snippet:

```md
Use the `sqlite_lab` MCP server whenever the task needs database schema context or SQL-backed record lookup.
```

## Gemini CLI

Reference:

- https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/configuration.md

Recommended setup command:

```bash
gemini mcp add sqlite-lab /ABSOLUTE/PATH/TO/python /ABSOLUTE/PATH/TO/implementation/mcp_server.py --description "SQLite lab FastMCP server" --timeout 10000
```

Then verify:

```bash
gemini mcp list
gemini --allowed-mcp-server-names sqlite-lab --yolo -p "Use the sqlite-lab MCP server and show me the top 2 students by score."
```

Alternative settings fragment:

```json
{
  "mcpServers": {
    "sqlite-lab": {
      "command": "python",
      "args": ["/ABSOLUTE/PATH/TO/implementation/mcp_server.py"],
      "cwd": "/ABSOLUTE/PATH/TO/implementation",
      "timeout": 10000,
      "trust": false
    }
  }
}
```

Tips:

- Prefer `gemini mcp add` over manual JSON edits.
- Avoid underscores in Gemini MCP server aliases.
- Use the exact Python interpreter where `fastmcp` is installed.
- `gemini mcp list` should show the server as `Connected`.

## Antigravity

Antigravity’s MCP behavior changes quickly. In many current setups, the config file is `mcp_config.json` and uses a shape similar to Gemini CLI.

Illustrative config:

```json
{
  "mcpServers": {
    "sqlite-lab": {
      "command": "python",
      "args": ["/ABSOLUTE/PATH/TO/implementation/mcp_server.py"],
      "cwd": "/ABSOLUTE/PATH/TO/implementation"
    }
  }
}
```

Tips:

- Verify the actual config location from the product UI in your installed version.
- Prefer stdio first; it is easier for a classroom lab than remote auth.
- Avoid hardcoding secrets into raw JSON files.

## Inspector

Reference:

- https://modelcontextprotocol.io/docs/tools/inspector

Typical local run:

```bash
mkdir -p .npm-cache
NPM_CONFIG_CACHE="$PWD/.npm-cache" npx -y @modelcontextprotocol/inspector /ABSOLUTE/PATH/TO/python /ABSOLUTE/PATH/TO/implementation/mcp_server.py
```

If you keep the reference implementation structure, you can also run:

```bash
cd implementation
./start_inspector.sh
```

Checklist:

- tools appear with schemas
- resources appear
- valid tool call succeeds
- invalid tool call returns a clear error
