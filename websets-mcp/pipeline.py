"""Search pipeline: query generation, Exa search, entity extraction."""

from __future__ import annotations

import json
import os
from typing import Union

import anthropic
from exa_py import Exa

from schemas import Person, Company
import storage

ANTHROPIC_MODEL = "claude-sonnet-4-6"


def _get_anthropic_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def _get_exa_client() -> Exa:
    return Exa(api_key=os.environ["EXA_API_KEY"])


# ── Step 1: Generate search queries ─────────────────────────────────────────


def generate_queries(criteria: str, entity_type: str) -> list[str]:
    """Use Claude to generate 5-10 targeted Exa search queries from criteria."""
    client = _get_anthropic_client()
    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": (
                    f"You are a search query expert. Generate 5 to 10 targeted search queries "
                    f"optimized for Exa's semantic search engine.\n\n"
                    f"Entity type: {entity_type}\n"
                    f"Search criteria: {criteria}\n\n"
                    f"Return ONLY a JSON array of query strings, nothing else. Example:\n"
                    f'["query one", "query two", "query three"]'
                ),
            }
        ],
    )
    text = response.content[0].text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    return json.loads(text)


# ── Step 2: Run Exa searches ────────────────────────────────────────────────


def run_exa_searches(queries: list[str], num_results: int = 10) -> list[dict]:
    """Execute each query against Exa and collect raw results with full page contents."""
    exa = _get_exa_client()
    all_results = []
    seen_urls = set()

    for query in queries:
        try:
            response = exa.search_and_contents(
                query,
                type="auto",
                num_results=num_results,
                text=True,
            )
            for result in response.results:
                if result.url not in seen_urls:
                    seen_urls.add(result.url)
                    all_results.append(
                        {
                            "url": result.url,
                            "title": result.title,
                            "text": (result.text or "")[:4000],  # cap length for context window
                        }
                    )
        except Exception as exc:
            # Log but don't abort the whole pipeline for one failed query
            print(f"[pipeline] Exa search failed for query '{query}': {exc}")

    return all_results


# ── Step 3: Extract entities ─────────────────────────────────────────────────


_PERSON_SCHEMA = """\
{
  "name": "string (required)",
  "linkedin_url": "string or null",
  "github_username": "string or null",
  "title": "string or null",
  "company": "string or null",
  "seniority": "string or null — one of: junior, mid, senior, lead, director, vp, c-level, founder",
  "signals": ["list of evidence strings — why this person matches the criteria"],
  "source_urls": ["list of URLs where this person was found"]
}"""

_COMPANY_SCHEMA = """\
{
  "name": "string (required)",
  "domain": "string or null — company website domain",
  "description": "string or null",
  "industry": "string or null",
  "size_range": "string or null — e.g. 1-10, 11-50, 51-200, 201-500, 501-1000, 1001-5000, 5000+",
  "tech_signals": ["list of technology/evidence strings"],
  "source_urls": ["list of URLs where this company was found"]
}"""


def extract_entities(
    raw_results: list[dict], criteria: str, entity_type: str
) -> list[Union[Person, Company]]:
    """Use Claude to extract structured entity records from raw search results."""
    if not raw_results:
        return []

    schema = _PERSON_SCHEMA if entity_type == "person" else _COMPANY_SCHEMA
    entity_cls = Person if entity_type == "person" else Company

    # Build a condensed view of results for the prompt
    sources_text = ""
    for i, r in enumerate(raw_results[:30], 1):  # cap at 30 to fit context
        sources_text += f"\n--- Source {i}: {r['url']} ---\nTitle: {r['title']}\n{r['text'][:2000]}\n"

    client = _get_anthropic_client()
    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": (
                    f"You are a data extraction expert. Extract all {entity_type} entities from "
                    f"the following web search results that match this criteria:\n\n"
                    f"Criteria: {criteria}\n\n"
                    f"For each entity, return a JSON object matching this schema:\n{schema}\n\n"
                    f"Return ONLY a JSON array of entity objects. If no entities are found, return [].\n\n"
                    f"Search results:\n{sources_text}"
                ),
            }
        ],
    )

    text = response.content[0].text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    records = json.loads(text)
    return [entity_cls.from_dict(r) for r in records]


# ── Full pipeline ────────────────────────────────────────────────────────────


def run_pipeline(webset: dict, db_path: str | None = None) -> list[dict]:
    """Execute the full search pipeline for a webset and store results.

    Returns a list of entity dicts that were stored.
    """
    kwargs = {"db_path": db_path} if db_path else {}

    webset_id = webset["id"]
    criteria = webset["criteria"]
    entity_type = webset["entity_type"]

    # Create a run record
    run_id = storage.create_run(webset_id, **kwargs)

    try:
        # Step 1 — generate queries
        queries = generate_queries(criteria, entity_type)

        # Step 2 — run Exa searches
        raw_results = run_exa_searches(queries)

        # Step 3 — extract entities
        entities = extract_entities(raw_results, criteria, entity_type)

        # Step 4 — assign webset_id and store
        for entity in entities:
            entity.webset_id = webset_id

        new_count = storage.store_results(webset_id, run_id, entities, **kwargs)

        # Finish run
        storage.finish_run(run_id, new_count, "completed", **kwargs)

        return [e.to_dict() for e in entities]

    except Exception as exc:
        storage.finish_run(run_id, 0, f"failed: {exc}", **kwargs)
        raise
