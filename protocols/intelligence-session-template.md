# Intelligence Edge-Finding Session Template

**Session type:** OSINT/HUMINT edge exploration
**Prerequisite:** Resolved entity data from OpenPlanter or equivalent
**Duration:** 45-90 minutes
**Participants:** Human analyst (tether holder) + LLM (explorer)

---

## Pre-Session Setup

### 1. Load Context

Before beginning, prepare a **context packet** from your structured analysis layer:

```
ENTITIES:       List of resolved entities (people, orgs, locations, assets)
RELATIONSHIPS:  Known connections with types and confidence levels
TIMELINE:       Key events in chronological order
GAPS:           What's missing? What doesn't connect? What changed unexpectedly?
HUMINT NOTES:   Field observations, analyst intuitions, "something feels wrong" signals
```

**Critical:** Include the gaps. The gaps are where edge-finding does its best work. If the ontology is complete and confident, you don't need this — use standard analysis.

### 2. Select Models

Run edge-finding across **3+ LLMs independently** for maximum divergence signal:

| Model | Strength | Blind Spot |
|-------|----------|------------|
| Claude (Anthropic) | Nuanced relational reasoning, ethical awareness | May over-hedge on uncertainty |
| GPT (OpenAI) | Broad associative range, strong narrative construction | Can over-commit to plausible stories |
| Qwen (Alibaba/Cerebras) | Different cultural training distribution, technical depth | Different geographic/institutional biases |
| Local model (Ollama) | No API data exposure, different parameter scale | Smaller associative range |

The disagreements between models are signal. Same inputs, different associations = different slices of the world's information being surfaced.

### 3. Define Scope

What is the investigation about? Write one sentence:

> "We are investigating [WHAT] involving [WHO] in the context of [DOMAIN/TIMEFRAME]."

This anchors the tether. The AI ranges from here but can always find its way back.

---

## Session Protocol

### Phase 1: Scatter (15-20 min)

**Prompt pattern:**

> "Edge bird: here are [N] entities connected to [this network/investigation/pattern]. The known links are [summary]. The gaps are [summary].
>
> Scatter probability. What unlikely connections might exist that we haven't named? Don't explain — just report what you find at the edges."

**What to collect:**
- Fragments — partial patterns, unlikely associations
- Inversions — "what if the relationship direction is reversed?"
- Category gaps — "what entity type is missing from this model?"
- Temporal anomalies — "what if the timeline doesn't mean what we think?"

**Analyst role:** Don't redirect. Don't evaluate yet. Collect everything. Your job is to hold the tether, not steer.

Run this phase independently on each model. Do not share one model's output with another yet.

---

### Phase 2: Cross-Model Divergence Analysis (10-15 min)

Compare fragments across models:

```
CONVERGENT FRAGMENTS:    Appeared across 2+ models → Higher signal
UNIQUE FRAGMENTS:        Appeared in only one model → Either noise or unique insight
CONTRADICTORY FRAGMENTS: Models disagree → The disagreement space is analytically rich
ABSENT PATTERNS:         Something you expected to see but no model surfaced → Interesting absence
```

**Key question:** Where do the models *disagree*? That's where unnamed patterns are most likely hiding.

Create a **divergence map**:

| Fragment | Claude | GPT | Qwen | Local | Assessment |
|----------|--------|-----|------|-------|------------|
| [fragment] | Y/N | Y/N | Y/N | Y/N | convergent / unique / contradictory |

---

### Phase 3: Dark Edges (10-15 min)

Now probe the risks — what the structured analysis might be getting wrong.

**Prompt pattern:**

> "Dark edges: what are we wrong about in this entity model? What assumption is incorrect? What entity category is missing? What if the relationship we think is causal is actually coincidental — or the coincidence is actually causal?
>
> Be specific. Name the assumption and name the alternative."

**What to collect:**
- Challenged assumptions
- Missing entity types
- Reversed causality hypotheses
- Temporal reframings
- Actor misidentifications

**Analyst role:** This is where domain expertise matters most. Some dark edges will be trivially wrong. Some will make your stomach drop. Note which is which and *why* you know.

---

### Phase 4: Constraint Storm (10-15 min)

Map the hard boundaries of the investigation subject (not *your* investigation — the *target's* constraints).

**Prompt pattern:**

> "Constraint storm: map the binding constraints on this network/entity/operation. What actually limits their movement? What resources are finite? What can't be faked? What leaves traces they can't erase?
>
> The binding constraint is probably not the obvious one. Find it."

**What to collect:**
- Resource constraints (money, people, time, logistics)
- Structural constraints (geography, jurisdiction, technology)
- Identity constraints (cover stories have limits, relationships leave traces)
- Information constraints (what they can't know, what they must know)

**Binding constraint identification:** Which constraint, if removed, would change everything? That's where the investigation should focus.

---

### Phase 5: Fragment Validation & Routing (10-15 min)

Now the analyst evaluates. For each surviving fragment:

**Validation questions:**
1. Is this consistent with HUMINT? Does field intelligence support or contradict it?
2. Is this testable? Can we look for evidence without alerting the target?
3. Is this new? Does this point somewhere the structured analysis hasn't looked?
4. Is this dangerous? Could acting on this fragment cause harm if it's wrong?

**Routing decisions:**

| Fragment Type | Route To |
|---------------|----------|
| Validated lead | OpenPlanter — new search pattern |
| New entity type | Ontology — new category definition |
| New relationship type | Ontology — new edge type definition |
| Unresolved question | Next edge-finding session |
| Noise | Archive with "noise" tag (may become signal later) |
| Named pattern | Unnamed Pattern Registry — track its evolution |

---

## Post-Session

### 1. Fragment Report

Document all surviving fragments with:
- Source model(s)
- Convergence status (convergent / unique / contradictory)
- Validation status (validated / testable / speculative / noise)
- Routing decision
- Analyst confidence (high / medium / low / intuition-only)

### 2. Ontology Feedback

Did this session reveal:
- Entity types that should exist but don't?
- Relationship types that need names?
- Properties that should be tracked but aren't?

Feed these back to the ontology layer. The system learns to see what it couldn't previously name.

### 3. HUMINT Integration

Did any fragments:
- Explain a field observation that was previously unexplained?
- Contradict something an informant reported? (valuable — test both)
- Suggest a new collection requirement?

### 4. Schedule Next Session

Edge-finding is iterative. Each session changes what the next one can see. Schedule the next session after:
- New data is ingested (OpenPlanter ran new searches)
- Ontology was updated (new types or relationships)
- HUMINT provides new context
- Previous fragments have been tested

---

## Session Anti-Patterns

**Don't do these:**

- **Steering the AI toward your hypothesis** — You're confirming, not exploring. Let the scatter work.
- **Running one model only** — You're seeing one slice of associative space. Divergence is the signal.
- **Skipping dark edges** — The uncomfortable possibilities are where the value is. If it's comfortable, you haven't gone far enough.
- **Treating fragments as findings** — Fragments are hypotheses. They need validation before they become intelligence.
- **Skipping HUMINT integration** — The human analyst isn't a consumer of AI output. They're the judgment layer that makes edge exploration safe and productive.
- **Ignoring noise** — Today's noise may be tomorrow's signal. Archive, don't delete.

---

*The flock expands from the edge, not the center.*
