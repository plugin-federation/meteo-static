# meteo-static

Mock meteorological MCP server that serves fixed weather data for locations.
Used to dogfood Plugin Federation shared Actions (tool listing, schema
validation, Nexus catalog + judges, embeddings, functional evals).

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

All shared Actions come from **`plugin-federation/actions`** (not the retired
`plugin-federation-actions` repo).

| Job | Purpose |
|-----|---------|
| `tools-list-validate` | Export `tools/list` + SEP-986 / PF structural validation |
| `nexus-catalog` | OIDC → catalog record + tool embeddings + LLM-as-judge |
| `evals` | Anthropic-format functional evals (`evals/evaluations.xml`) |

## Status

- **Working** — both transports functional
- **Tools** — mock weather tools with JSON schemas
- **CI** — entirely on `plugin-federation/actions`

## Nexus pipeline (nonprod dogfood)

GitHub Actions exchanges an OIDC ID token for a short-lived Nexus JWT, records
the exported `tools/list` catalog, optionally embeds tools (name + description),
and runs tenant judges.

| Variable / secret | Purpose |
|-------------------|---------|
| `NEXUS_URL` | `https://api.nonprod.plugin-federation.com` |
| `NEXUS_OIDC_AUDIENCE` | Must match Nexus `NEXUS_OIDC_GITHUB_AUDIENCE` |
| `TENANT_ID` | Target tenant UUID |
| `MCP_SOURCE_ID` | Stable tool source UUID for this server |
| `EMBEDDING_MODEL` | Optional; default `text-embedding-3-small` |
| `EMBEDDING_PROVIDER` | Optional; default `openai` |
| `XAI_API_KEY` | Judge / functional eval model |
| `OPENAI_API_KEY` | Embeddings (when using the OpenAI provider) |

Workflow job `nexus-catalog` uses:

- `plugin-federation/actions/nexus-oidc-exchange`
- `plugin-federation/actions/mcp-tool-judge-pipeline` (catalog + embed + judges)

Functional evals use:

- `plugin-federation/actions/anthropic-mcp-eval`

Requires `permissions: id-token: write`. Trust policy is registered in Nexus
(immutable `repository_id`).
