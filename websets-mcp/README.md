# websets-mcp

An MCP server that replicates [Exa Websets](https://exa.ai) — named, saveable searches that return structured lists of **people** or **companies** from web sources, with HubSpot and Google Sheets sync.

## How it works

1. **Create a webset** — define a named search with natural-language criteria and an entity type (`person` or `company`).
2. **Run the webset** — the server uses Claude to generate targeted search queries, executes them against Exa's semantic search API, extracts structured entities with Claude, deduplicates against SQLite, and returns results.
3. **Export** — push results to HubSpot as contacts/companies, or export to a Google Sheet.

## MCP Tools

| Tool | Description |
|------|-------------|
| `create_webset(name, criteria, entity_type)` | Save a named search definition |
| `run_webset(name)` | Execute the search pipeline and return results |
| `list_websets()` | List all saved websets |
| `get_webset_results(name)` | Get last run results for a webset |
| `export_to_sheets(name, sheet_id)` | Export results to Google Sheets |
| `push_to_hubspot(name)` | Push results to HubSpot as contacts or companies |
| `delete_webset(name)` | Remove a webset and its results |

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy the example env file and fill in your API keys:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `EXA_API_KEY` | Yes | Exa API key from [exa.ai](https://exa.ai) |
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for Claude |
| `HUBSPOT_API_KEY` | No | HubSpot private app access token (for `push_to_hubspot`) |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | No | Google service account JSON (for `export_to_sheets`) |

### 3. Add to Claude Desktop

Add the server to your Claude Desktop configuration file (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "websets": {
      "command": "python",
      "args": ["/absolute/path/to/websets-mcp/server.py"],
      "env": {
        "EXA_API_KEY": "your_exa_api_key",
        "ANTHROPIC_API_KEY": "your_anthropic_api_key",
        "HUBSPOT_API_KEY": "your_hubspot_api_key",
        "GOOGLE_SERVICE_ACCOUNT_JSON": "{...}"
      }
    }
  }
}
```

Or, if you use a `.env` file, just set the command and args — the server loads `.env` automatically via `python-dotenv`.

## Example usage

Once connected through Claude Desktop:

> **You:** Create a webset called "ai-infra-founders" to find founders and CTOs of AI infrastructure startups that have raised Series A or B funding.

> **Claude:** *(calls `create_webset`)* Created webset "ai-infra-founders" with entity type "person".

> **You:** Run it.

> **Claude:** *(calls `run_webset`)* Found 12 results including...

> **You:** Push those to HubSpot.

> **Claude:** *(calls `push_to_hubspot`)* Pushed 12 contacts to HubSpot.

> **You:** Also export to my Google Sheet `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms`.

> **Claude:** *(calls `export_to_sheets`)* Exported 12 rows to the spreadsheet.

## Entity schemas

### Person
`name`, `linkedin_url`, `github_username`, `title`, `company`, `seniority`, `signals`, `source_urls`, `date_captured`

### Company
`name`, `domain`, `description`, `industry`, `size_range`, `tech_signals`, `source_urls`, `date_captured`

## Architecture

```
server.py          → MCP server entry point (FastMCP)
pipeline.py        → Search pipeline: query gen → Exa search → entity extraction
storage.py         → SQLite operations (websets, runs, results tables)
hubspot_sync.py    → HubSpot CRM push
sheets_sync.py     → Google Sheets export
schemas.py         → Person and Company dataclasses
```
