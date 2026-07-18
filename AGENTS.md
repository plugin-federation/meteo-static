# meteo-static — Agent Guide

## Purpose

Mock meteorological MCP server that serves fixed weather data for locations. Used to validate GitHub Actions that check MCP server tooling (tool listing, schema validation, transport support).

## Tools

| Tool | Description |
|------|-------------|
| `get_weather` | Get current weather for a city |
| `get_forecast` | Get a 3-day forecast for a city |
| `list_cities` | List all supported cities |

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

## GitHub Actions

CI workflows under `.github/workflows/` validate:

- Python linting (ruff)
- Type checking (mypy)
- Tool listing via the MCP protocol

## Key files

| Path | Role |
|------|------|
| `src/server.py` | MCP server entry point |
| `pyproject.toml` | Python project config |
| `requirements.txt` | Dependencies |
| `.github/workflows/` | CI lint + type-check + tool validation |

## Status

- **Working** — both transports functional
- **Tools** — 3 tools with complete JSON schemas
- **CI** — lint, type-check, tool validation via plugin-federation-actions

## Depends on

- **plugin-federation-actions** — CI workflows for MCP server validation

## Related

- [./meteo-dynamic/AGENTS.md](./meteo-dynamic/AGENTS.md) — companion computation server
- [./plugin-federation-actions/AGENTS.md](./plugin-federation-actions/AGENTS.md) — shared CI actions
