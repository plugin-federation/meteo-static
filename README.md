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
| `nexus-catalog` | OIDC → catalog, schema verify, selection-surface embeddings, LLM-as-judge |
| `evals` | Anthropic-format functional evals (`evals/evaluations.xml`) |

## Status

- **Working** — both transports functional
- **Tools** — mock weather tools with JSON schemas
- **CI** — entirely on `plugin-federation/actions`

## Nexus pipeline (nonprod dogfood)

GitHub Actions exchanges an OIDC ID token for a short-lived Nexus JWT, records
the exported `tools/list` catalog, schema-verifies it against plugin draft pins,
embeds the model-visible selection surface (name + description + input schema),
and runs tenant judges. Embed failures do not fail the judge step. Similarity
reports are derived by Nexus from a registered semantic-analysis profile, not
in this repository.

A tenant admin must register a `semantic-analysis-profile/v1` whose
`profileVersion` and `model` match `embedding-model` (`text-embedding-3-small`)
and whose `dimensions` match the provider output (1536 for that model unless
shortened). CI uses `plugin_author` and cannot create that profile.

| Variable / secret | Purpose |
|-------------------|---------|
| `NEXUS_URL` | `https://api.nonprod.plugin-federation.com` |
| `NEXUS_OIDC_AUDIENCE` | Must match Nexus `NEXUS_OIDC_GITHUB_AUDIENCE` |
| `TENANT_ID` | Target tenant UUID |
| `MCP_SOURCE_ID` | Stable tool source UUID for this server |
| `XAI_API_KEY` | Judge model and functional evals |
| `OPENAI_API_KEY` | Tool embeddings (`text-embedding-3-small`) |

Workflow job `nexus-catalog` uses:

- `plugin-federation/actions/nexus-oidc-exchange`
- `plugin-federation/actions/mcp-tool-judge-pipeline` (catalog + schema verify + embed + judges)

Functional evals use:

- `plugin-federation/actions/anthropic-mcp-eval`

Requires `permissions: id-token: write`. Trust policy is registered in Nexus
(immutable `repository_id`).
