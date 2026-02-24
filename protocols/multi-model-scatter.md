# Multi-Model Scatter Protocol

**Purpose:** Systematically exploit LLM associative divergence for intelligence discovery
**Prerequisite:** Entity data loaded, 3+ LLM providers configured
**Core principle:** Different training distributions = different edges visible

---

## Why Multiple Models

Every LLM encodes a vast associative network learned from its training data. When you ask a model "what unlikely connection might exist here?", it draws from its specific distribution of the world's information.

- **Different training corpora** surface different associations
- **Different architectures** weight relationships differently
- **Different alignment training** creates different suppression patterns (what the model *won't* say is also signal)

**The disagreement space between models is where unnamed patterns hide.**

When three models converge on an unlikely association: strong signal.
When one model sees something the others don't: either noise or unique insight — the analyst decides.
When models contradict each other: the contradiction itself is analytically valuable.

---

## Setup

### Model Configuration

Use OpenPlanter's provider-agnostic model layer, or configure independently:

```
MODEL_A:  Anthropic Claude (claude-opus-4-6)
MODEL_B:  OpenAI GPT (gpt-5.2)
MODEL_C:  Cerebras/Qwen (qwen-3-235b)
MODEL_D:  Ollama local (llama3.2 or similar)
```

Minimum 3 models. 4+ recommended. Include at least one local model for:
- Data that shouldn't leave your environment
- Baseline from a differently-scaled model
- Checking whether associations require frontier-model scale

### Context Packet

Identical context goes to each model. Same entities, same relationships, same gaps, same HUMINT notes. The *only* variable is the model.

```
CONTEXT PACKET (identical to all models):
├── entities.json         # Resolved entities from OpenPlanter
├── relationships.json    # Known connections with types
├── timeline.json         # Chronological events
├── gaps.md               # Missing connections, unexplained patterns
└── humint_notes.md       # Field observations, analyst intuitions
```

---

## Execution

### Step 1: Independent Scatter

Run the same scatter prompt against each model independently. **Do not share one model's output with another.**

**Scatter prompt template:**

```
Edge bird: I'm going to share an entity network from an OSINT investigation.
Your task is to scatter probability — explore the unlikely connection space.
Do not explain or justify. Report fragments: partial patterns, inversions,
category gaps, temporal anomalies, things that "remind you of" something
you can't quite name.

[PASTE CONTEXT PACKET]

What unlikely connections might exist that haven't been named?
What's at the edges?
```

Collect raw output from each model. Tag each fragment with its source model.

### Step 2: Fragment Extraction

From each model's output, extract discrete fragments. One fragment = one association, one inversion, one observation. Format:

```
FRAGMENT ID:    scatter-001
SOURCE MODEL:   Claude
CONTENT:        [the fragment]
ENTITY REFS:    [which entities from the context it touches]
TYPE:           association / inversion / category_gap / temporal / metaphor / other
```

### Step 3: Divergence Matrix

Build the comparison:

| Fragment ID | Content Summary | Claude | GPT | Qwen | Local | Pattern |
|-------------|----------------|--------|-----|------|-------|---------|
| scatter-001 | [summary] | X | X | - | - | Convergent (2/4) |
| scatter-002 | [summary] | X | - | - | - | Unique |
| scatter-003 | [summary] | - | X | X | X | Convergent (3/4) |
| scatter-004 | [summary] | X | - | X | - | Contradicted by GPT |

### Step 4: Divergence Analysis

**Convergent fragments (2+ models):**
- Higher confidence these represent real associations in the data
- Priority for validation
- Ask: why did multiple models see this? What's in the training data?

**Unique fragments (1 model only):**
- Could be noise OR unique insight from that model's training distribution
- Ask: does this model have training data the others don't? (e.g., Qwen may surface associations from Chinese-language sources invisible to English-dominant models)
- Flag for analyst evaluation — domain expertise decides

**Contradictory fragments:**
- Most analytically valuable category
- One model says A→B, another says A→C for the same entities
- The contradiction reveals different possible interpretations of the same data
- Ask: what would need to be true for EACH model's version to be correct?

**Absent patterns:**
- What did you expect to see that NO model surfaced?
- Absence across all models suggests either: (a) the association genuinely doesn't exist, or (b) all models share a training blind spot in this area
- If (b): this is where HUMINT becomes critical

---

## Bias Cartography

Over multiple sessions, track which models consistently surface which types of associations:

```
BIAS MAP (builds over time):
├── Model A tends to: [over-associate financial entities with geographic patterns]
├── Model B tends to: [construct narrative chains, sometimes over-fitting causality]
├── Model C tends to: [surface cross-cultural associations others miss]
└── Model D tends to: [miss complex multi-hop relationships, strong on direct links]
```

This map becomes a tool for **model selection**. When investigating financial networks, you might weight Model A's fragments higher. When investigating cross-jurisdictional patterns, Model C's unique fragments deserve more attention.

---

## Integration with OpenPlanter

OpenPlanter already supports multiple LLM providers. The scatter protocol can be partially automated:

```
1. OpenPlanter resolves entities → exports context packet
2. Scatter prompt generated from context packet
3. Same prompt sent to N configured models
4. Fragment extraction (manual or semi-automated)
5. Divergence matrix built
6. Human analyst evaluates
7. Validated fragments → new OpenPlanter search patterns
```

Steps 1-3 can run through OpenPlanter's recursive engine.
Steps 4-5 can be tooling-assisted but need human review.
Steps 6-7 require human judgment — this is the elastic tether.

---

## Worked Example: Fragment Divergence

**Context:** Network of 12 entities around a government procurement pattern.

**Claude fragment:** "The timing gap between contract award and subcontractor registration suggests the subcontractor entity may have been created *for* this contract, not before it."

**GPT fragment:** "The subcontractor's registered agent shares an address with Entity 7's former legal counsel — dissolved 18 months prior."

**Qwen fragment:** "Similar procurement patterns in [different jurisdiction] involved shell entities with exactly this registration-to-award timeline."

**Local model:** No relevant fragment on this cluster.

**Divergence analysis:**
- Claude sees temporal anomaly (creation timing)
- GPT sees relational link (shared address → dissolved counsel)
- Qwen sees cross-jurisdictional pattern match
- All three are touching the same underlying pattern from different angles
- Convergence diagnosis: **strong signal** — three models see different facets of what may be the same thing

**Routing:** Feed back to OpenPlanter as a new search pattern: look for entity creation dates within 90 days of contract awards, cross-referenced with dissolved entities sharing addresses.

---

## Limitations

- **Compute cost:** Running 3-4 models on every investigation is expensive. Use scatter sessions selectively — when structured analysis has stalled or gaps are persistent.
- **Prompt sensitivity:** Different phrasings produce different fragments. Standardize the scatter prompt template but expect variation.
- **Temporal lag:** Model training data has a cutoff. Very recent events won't appear in associative space. This is where HUMINT fills the gap.
- **False convergence:** Multiple models may converge on a wrong association if it's prominent in all their training data. Convergence increases confidence but doesn't guarantee truth.

---

*Different lenses on the same data. The edges are where they disagree.*
