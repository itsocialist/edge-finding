# Edge Bird — Development Backlog

## Priority: High

### Dark Edges Evidence Requirement
- **Problem:** Claude's dark edges at 0.7 still produce conspiracy-tier claims (state actors, backdoors, counter-intelligence) without evidence
- **Fix:** Modify `dark_edges` system prompt to require evidence citation for each claim
- **Scope:** `edgebird/prompts/dark_edges.py` or equivalent prompt template
- **Discovered:** Session 2026-02-24, IAG investigation

### Cross-Session Fragment Search
- **Problem:** Each session is isolated. 156 fragments across 12 sessions can't be queried or compared
- **Fix:** Build fragment database (SQLite or YAML index) with search CLI command
- **Scope:** New `edgebird/store.py` + `edgebird fragment search <query>` command
- **Value:** Enables pattern mining across investigations over time

### Auto-Ingest Pipeline
- **Problem:** Manually converting OpenPlanter findings to Edge Bird context YAML is tedious
- **Fix:** Script to convert OpenPlanter `findings.json` → Edge Bird context YAML automatically
- **Scope:** `scripts/openplanter_to_edgebird.py`
- **Partially done:** Manual conversions exist as templates in `contexts/`

## Priority: Medium

### Fragment Scoring Rubric
- **Problem:** Fragments assessed qualitatively (analyst judgment only)
- **Fix:** Add scoring dimensions: specificity (1-5), testability (1-5), cross-model agreement (bool), novelty (1-5)
- **Scope:** Update `edgebird validate` to include scoring prompts

### Third Model Support
- **Problem:** Only tested with Claude + GPT-4o. A third perspective strengthens convergence
- **Fix:** Test with Gemini, Llama 3 (via Ollama), or Mistral
- **Scope:** Already supported by litellm — just needs testing and documentation

### Fragment Linking
- **Problem:** Fragment A from scatter may connect to Fragment B from constraint storm, but tool doesn't surface these
- **Fix:** Post-phase analysis that identifies thematic links between fragments within a session
- **Scope:** New `edgebird link <session-id>` command

### Divergence Visualization
- **Problem:** Multi-model divergence is described in text only
- **Fix:** Build web UI to visualize fragment clusters by model, phase, and theme
- **Scope:** Part of future dashboard — see UI section below

## Priority: Low

### Historical Validation Test
- **Problem:** No proof that edge-finding discovers things that structured analysis misses
- **Fix:** Take a known-outcome case, feed pre-discovery data into Edge Bird, check if fragments point toward known answer
- **Scope:** Research exercise, not code change

### Temperature Sweep Automation
- **Problem:** Manually running at different temperatures to compare
- **Fix:** `edgebird sweep <context> --temps 0.5,0.7,1.0` runs all temps and produces comparison
- **Scope:** CLI wrapper around existing `run` command

---

## UI Dashboard (Future)

Build a local web app that reads session directories and provides:
- Fragment browser with filtering (by phase, model, temperature, investigation)
- Multi-model divergence visualization
- Interactive validation (accept/reject/annotate fragments)
- Cross-session fragment search
- Network graph visualization of entity relationships
- Session comparison view (same data, different parameters)

---

## Completed (This Session)

- [x] Default temperature changed from 1.0 → 0.7 (`cli.py`)
- [x] Build backend fixed in `pyproject.toml` (setuptools.build_meta)
- [x] Package discovery added to `pyproject.toml`
- [x] `.gitignore` updated for sessions/, contexts/, .venv/
- [x] Multi-model scatter validated (Claude + GPT-4o)
- [x] Temperature comparison (1.0 vs 0.7) — 0.7 confirmed as better default
- [x] 3 investigations run: IAG Network, Linux AI Market, Hovland Dossier
- [x] 12 sessions, 156 fragments, 16 promoted findings
