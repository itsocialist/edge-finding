"""WebSets MCP Server — named, saveable searches that return structured lists
of people or companies from web sources, with HubSpot and Google Sheets sync."""

from __future__ import annotations

import json
import os
import sys

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Ensure the package directory is importable
sys.path.insert(0, os.path.dirname(__file__))

import storage
import pipeline
import hubspot_sync
import sheets_sync

load_dotenv()

mcp = FastMCP(
    "websets-mcp",
    instructions=(
        "WebSets MCP server — create named, saveable searches that find people "
        "or companies from web sources.  Search results can be exported to "
        "Google Sheets or pushed to HubSpot."
    ),
)

# Initialise the database on startup
storage.init_db()


# ── Tools ────────────────────────────────────────────────────────────────────


@mcp.tool()
def create_webset(name: str, criteria: str, entity_type: str) -> str:
    """Create a named webset (saveable search definition).

    Args:
        name: Unique name for this webset.
        criteria: Natural-language description of what to search for.
        entity_type: Either "person" or "company".
    """
    if entity_type not in ("person", "company"):
        return json.dumps({"error": "entity_type must be 'person' or 'company'"})
    try:
        webset = storage.create_webset(name, criteria, entity_type)
        return json.dumps({"status": "created", "webset": webset})
    except ValueError as exc:
        return json.dumps({"error": str(exc)})


@mcp.tool()
def run_webset(name: str) -> str:
    """Execute the search pipeline for a webset and return results.

    The pipeline:
    1. Generates targeted search queries from the criteria using Claude
    2. Runs each query against Exa's semantic search engine
    3. Extracts structured entities from raw results using Claude
    4. Deduplicates and stores results in SQLite

    Args:
        name: Name of the webset to run.
    """
    webset = storage.get_webset(name)
    if not webset:
        return json.dumps({"error": f"Webset '{name}' not found"})

    try:
        results = pipeline.run_pipeline(webset)
        return json.dumps({
            "status": "completed",
            "webset": name,
            "results_count": len(results),
            "results": results,
        })
    except Exception as exc:
        return json.dumps({"error": f"Pipeline failed: {exc}"})


@mcp.tool()
def list_websets() -> str:
    """List all saved websets."""
    websets = storage.list_websets()
    return json.dumps({"websets": websets, "count": len(websets)})


@mcp.tool()
def get_webset_results(name: str) -> str:
    """Return the last stored results for a webset.

    Args:
        name: Name of the webset.
    """
    webset = storage.get_webset(name)
    if not webset:
        return json.dumps({"error": f"Webset '{name}' not found"})

    rows = storage.get_results(name)
    results = [r["data"] for r in rows]
    return json.dumps({
        "webset": name,
        "entity_type": webset["entity_type"],
        "results_count": len(results),
        "results": results,
    })


@mcp.tool()
def export_to_sheets(name: str, sheet_id: str) -> str:
    """Export webset results to a Google Sheet.

    Args:
        name: Name of the webset.
        sheet_id: Google Sheets spreadsheet ID.
    """
    webset = storage.get_webset(name)
    if not webset:
        return json.dumps({"error": f"Webset '{name}' not found"})

    entities = storage.get_results_as_entities(name)
    if not entities:
        return json.dumps({"error": f"No results for webset '{name}'. Run it first."})

    try:
        result = sheets_sync.export_to_sheets(entities, sheet_id, webset["entity_type"])
        return json.dumps({"status": "exported", **result})
    except Exception as exc:
        return json.dumps({"error": f"Sheets export failed: {exc}"})


@mcp.tool()
def push_to_hubspot(name: str) -> str:
    """Push webset results to HubSpot as contacts (person) or companies.

    Args:
        name: Name of the webset.
    """
    webset = storage.get_webset(name)
    if not webset:
        return json.dumps({"error": f"Webset '{name}' not found"})

    entities = storage.get_results_as_entities(name)
    if not entities:
        return json.dumps({"error": f"No results for webset '{name}'. Run it first."})

    try:
        result = hubspot_sync.push_entities(entities)
        return json.dumps({"status": "pushed", **result})
    except Exception as exc:
        return json.dumps({"error": f"HubSpot push failed: {exc}"})


@mcp.tool()
def delete_webset(name: str) -> str:
    """Delete a webset and all its results.

    Args:
        name: Name of the webset to delete.
    """
    deleted = storage.delete_webset(name)
    if deleted:
        return json.dumps({"status": "deleted", "name": name})
    return json.dumps({"error": f"Webset '{name}' not found"})


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
