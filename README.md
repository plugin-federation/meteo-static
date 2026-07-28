# meteo-static

Mock meteorological MCP server that serves fixed weather data for locations.
Used to validate GitHub Actions that check MCP server tooling (tool listing,
schema validation, transport support).

## Tools

| Tool | Description |
|------|-------------|
| `list_cities` | List all supported cities |
| `get_weather` | Get current weather for a city |
| `get_forecast` | Get a 3-day forecast for a city |

## Running

### STDIO (default)

```bash
pip install -r requirements.txt
python src/server.py
```

### Streamable HTTP

```bash
pip install -r requirements.txt
python src/server.py --transport http --port 8000
```

## Export tools/list (local)

```bash
pip install -r requirements.txt
python scripts/export_tools_list.py --output ci/tools-list.json
```

## Validate tools/list with Plugin Federation Action

```yaml
- uses: plugin-federation/actions/mcp-tools-list-validate@main
  with:
    tools-list-file: ci/tools-list.json
    profile: plugin-federation
```

CI job `tools-list-validate` exports the live catalog from this server and runs
that Action on every push/PR. See
[mcp-tools-list-validate](https://github.com/plugin-federation/actions/tree/main/mcp-tools-list-validate).

## GitHub Actions

| Job | Purpose |
|-----|---------|
| `tools-list-validate` | Export `tools/list` + SEP-986 / PF structural validation |
| `evals` | Anthropic-format functional evals (needs `XAI_API_KEY`) |

## Status

- **Working** — both transports functional
- **Tools** — 3 tools with JSON schemas
- **CI** — tools/list validate via `plugin-federation/actions`; evals via `plugin-federation-actions`
