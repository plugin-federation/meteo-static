# meteo-static — Agent Guide

## Purpose

Mock meteorological MCP server that serves fixed weather data for locations.
Used to dogfood Plugin Federation shared GitHub Actions (tool listing, schema
validation, Nexus catalog + judges, embeddings, functional evals).

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

CI workflows under `.github/workflows/` use **only**
[`plugin-federation/actions`](https://github.com/plugin-federation/actions):

- `mcp-tools-list-validate` — structural tools/list checks
- `nexus-oidc-exchange` + `mcp-tool-judge-pipeline` — catalog, schema verify,
  selection-surface embeddings (`text-embedding-3-small`), judges. Nexus owns
  similarity reports; embed errors do not fail judges.
- `anthropic-mcp-eval` — `evals/evaluations.xml` functional harness

Do **not** reference the retired `plugin-federation/plugin-federation-actions`
repository.

## Key files

| Path | Role |
|------|------|
| `src/server.py` | MCP server entry point |
| `pyproject.toml` | Python project config |
| `requirements.txt` | Dependencies |
| `evals/evaluations.xml` | Functional eval qa_pairs |
| `ci/tools-list.json` | Exported tools/list (artifact in CI) |
| `.github/workflows/ci.yml` | CI jobs |

## Status

- **Working** — both transports functional
- **Tools** — mock weather tools with JSON schemas
- **CI** — shared Actions from `plugin-federation/actions`

## Depends on

- **plugin-federation/actions** — shared CI Actions

## Related

- [meteo-dynamic](https://github.com/plugin-federation/meteo-dynamic) — companion computation server
- [plugin-federation/actions](https://github.com/plugin-federation/actions) — shared CI Actions
