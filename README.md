# meteo-static

Mock meteorological MCP server that serves fixed weather data for locations.
Used to validate GitHub Actions that check MCP server tooling (tool listing,
schema validation, transport support).

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

This repo has CI workflows under `.github/workflows/` that validate:

- Python linting (ruff)
- Type checking (mypy)
- Tool listing via the MCP protocol

## Status

- **Working** — both transports functional
- **Tools** — 3 tools with complete JSON schemas
