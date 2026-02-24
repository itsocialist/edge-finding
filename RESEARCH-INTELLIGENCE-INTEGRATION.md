# Research Intelligence Integration Proposal

**OpenPlanter + Edge Bird: A Two-Layer Intelligence Discovery System**

---

## The Thesis

Traditional intelligence analysis operates at the center of probability space — structured queries, entity resolution, pattern matching against known templates. This is necessary. It's also insufficient.

The connections that matter most are often the ones that live at the edges: low-probability links, unnamed patterns, relationships that no analyst would think to query because the *category* doesn't exist yet.

This proposal describes a system that combines **structured OSINT collection and ontology** (OpenPlanter) with **low-probability edge exploration** (Edge Bird) — using the weights and biases of LLMs not as flaws to mitigate, but as instruments to exploit for discovery.

No Palantir. No enterprise license. Entirely open-source.

---

## The Two Layers

### Layer 1: OpenPlanter — Collection, Entity Resolution & Ontology

**What it is:** An open-source recursive AI agent for investigative research across heterogeneous datasets. Ingests corporate records, campaign finance data, lobbying disclosures, government contracts, and performs cross-dataset entity resolution. Positions itself as the open-source alternative to Palantir — ontology-first design, governed data model, multi-LLM integration.

**Role in the system:** The hands AND the skeleton. Reaches into the raw data, then structures what it finds.

**Key capabilities for integration:**
- **Recursive decomposition** — breaks large investigations into sub-agent tasks (depth 4, 100 steps/cycle), parallelizing entity resolution and dataset linking
- **19-tool workspace** — file operations, shell execution, Exa-based web search, URL fetching for verification
- **Multi-LLM support** — OpenAI, Anthropic, Cerebras, Ollama (local) — provider-agnostic
- **Evidence chain construction** — doesn't just find connections, builds auditable evidence paths
- **Docker isolation** — agent shell commands sandboxed from host OS
- **Ontology-first design** — entity-relationship model as core abstraction, inspired by Palantir's architecture but MIT-licensed and self-hostable

**What it produces:** Resolved entities, cross-dataset links, evidence chains, structured investigation artifacts, entity-relationship models.

**What it misses:** It optimizes for *known categories* of connection. It finds what you tell it to look for, or what standard entity resolution surfaces. It does not explore the unnamed.

**Optional backing store:** For persistent graph storage and visualization beyond OpenPlanter's native model, open-source options include:
- **Neo4j Community Edition** — graph database, natural fit for entity-relationship models, Cypher query language, free visualization
- **NetworkX** (Python) — lightweight graph library for analysis and export
- **Apache TinkerPop / JanusGraph** — distributed graph for larger-scale investigations
- **Gephi** — open-source network visualization for analyst workbench

---

### Layer 2: Edge Bird — Low-Probability Exploration

**What it is:** A human-AI collaborative discovery practice that deliberately explores the edges of probability space — where unlikely connections live and unnamed patterns wait.

**Role in the system:** The wings. Ranges to corners no structured system would visit.

**Key capabilities for integration:**
- **Trigger protocols** — "edge bird," "scatter probability," "what's at the edges?" — coordination signals that shift LLM behavior from convergence to dispersion
- **Fragment-based discovery** — produces partial patterns, inversions, hidden questions, metaphors — material that accumulates and transforms
- **Dark edges** — unflinching examination of risks, failure modes, and blind spots
- **Constraint storms** — hard mapping of boundaries that reveals *binding* constraints (often not the obvious ones)
- **Elastic tether** — human holds one end, AI explores, neither lets go

**What it produces:** Fragments. Inversions. Questions hidden inside other questions. Connections between entities that no ontology would model because the *relationship type* doesn't have a name yet.

**What it misses:** It's a methodology, not a system. It has no data ingestion, no entity model, no audit trail. Its discoveries are only as good as the context it's given.

---

## The Integration: How They Work Together

### The Core Loop

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│   OSINT / HUMINT Data Sources                       │
│   (public records, social media, government         │
│    filings, human reports, field observations)      │
│                                                     │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│  LAYER 1: OpenPlanter                                │
│  ─────────────────                                   │
│  • Ingest heterogeneous datasets                     │
│  • Recursive entity resolution                       │
│  • Cross-dataset linking                             │
│  • Evidence chain construction                       │
│  • Ontology: entity-relationship model               │
│  • Surface known-pattern connections                 │
│                                                      │
│  Optional: Neo4j / NetworkX for persistent graph     │
│                                                      │
│  OUTPUT: Resolved entities + structured ontology     │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│  LAYER 2: Edge Bird                                  │
│  ────────────────                                    │
│  • Feed ontology context to edge-finding sessions    │
│  • Scatter probability across entity relationships   │
│  • Explore low-probability connection space          │
│  • Exploit LLM weights/biases for lateral links      │
│  • Human analyst holds the tether                    │
│                                                      │
│  OUTPUT: Fragments, inversions, unnamed patterns     │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│  FEEDBACK LOOP                                       │
│  ─────────────                                       │
│  • Edge fragments that survive validation →          │
│    new entity types / relationship types in          │
│    the OpenPlanter ontology                          │
│  • New ontology categories → new OpenPlanter         │
│    search patterns                                   │
│  • System learns to look for what it couldn't        │
│    previously name                                   │
└──────────────────────────────────────────────────────┘
```

### The Critical Innovation: LLM Bias as Instrument

Standard practice treats LLM biases — the weights that make certain associations more likely than others — as problems to mitigate. Hallucinations. Confabulations. Errors.

Edge Bird inverts this. **The biases ARE the discovery mechanism.**

Here's why this matters for intelligence analysis:

1. **LLMs encode vast associative networks.** When an LLM "hallucinates" a connection between a shipping company and a financial institution, it may be wrong about the *specific* link — but the association exists in its weights because *that pattern exists somewhere in its training data.* The signal is real even when the specific output is incorrect.

2. **Scatter probability exploits this.** Instead of asking "is entity A connected to entity B?" (center of distribution), you ask "what unlikely things does this entity constellation remind you of?" You're deliberately probing the long tail of the model's associative space.

3. **Multiple models see different edges.** OpenPlanter already supports multiple LLM providers. Running edge-finding across different models (GPT, Claude, Qwen, local models) produces *different* low-probability associations because they have different training distributions. The disagreements between models are signal.

4. **Human intelligence is the validator.** The human analyst — with domain expertise, contextual awareness, and intuition that no model has — holds the elastic tether. They recognize which fragments are noise and which are worth pursuing. HUMINT isn't just an input source; it's the *judgment layer* that makes edge exploration safe and productive.

---

## Concrete Architecture

### Data Flow

```
OSINT Sources                    HUMINT Sources
─────────────                    ──────────────
• Public records                 • Field reports
• Social media                   • Analyst observations
• Government filings             • Informant debriefs
• Corporate registries           • Cultural context
• News / media                   • Pattern intuitions
• Financial disclosures          • "Something feels wrong"
       │                                │
       └──────────┬─────────────────────┘
                  │
                  ▼
     ┌────────────────────────┐
     │    OpenPlanter Agent   │
     │    ────────────────    │
     │    Recursive ingestion │
     │    Entity resolution   │
     │    Evidence chains     │
     └───────────┬────────────┘
                 │
                 ▼
     ┌────────────────────────┐
     │    Ontology Layer      │
     │    ──────────────      │
     │    OpenPlanter's own   │
     │    ontology model      │
     │    + Neo4j (optional)  │
     │                        │
     │    Entities ←→ Rels    │
     │    Types, Properties   │
     │    Provenance, Access  │
     └───────────┬────────────┘
                 │
          ┌──────┴──────┐
          │             │
          ▼             ▼
   ┌─────────────┐ ┌─────────────────┐
   │ Structured  │ │ Edge-Finding    │
   │ Analysis    │ │ Sessions        │
   │ ──────────  │ │ ────────────    │
   │ Known-      │ │ Multi-model     │
   │ pattern     │ │ scatter across  │
   │ queries,    │ │ ontology,       │
   │ dashboards, │ │ fragment        │
   │ alerts      │ │ collection,     │
   │             │ │ dark edges,     │
   │             │ │ transformation  │
   └──────┬──────┘ └────────┬────────┘
          │                 │
          └────────┬────────┘
                   │
                   ▼
     ┌────────────────────────┐
     │  Analyst Workbench     │
     │  ──────────────────    │
     │  Structured findings   │
     │  + Edge fragments      │
     │  + Confidence scoring  │
     │  + Provenance trail    │
     │  + "Unnamed pattern"   │
     │    registry            │
     └────────────────────────┘
```

### Edge-Finding Session Protocol for Intelligence Analysis

**Setup:** Load relevant ontology subset into edge-finding context. Include entity profiles, known relationships, timeline, and — critically — the *gaps*. What's missing? What doesn't connect?

**Phase 1 — Scatter:**
> "Edge bird: here are 47 entities connected to this network. The known links are X, Y, Z. Scatter probability. What unlikely connections might exist that we haven't named?"

Run this across 3+ LLMs independently. Collect fragments from each.

**Phase 2 — Cross-Model Comparison:**
Which fragments appear across multiple models? (Higher signal.)
Which appear in only one? (Either noise or unique insight — human judges.)
Where do models *disagree*? (The disagreement space is where unnamed patterns hide.)

**Phase 3 — Dark Edges:**
> "Dark edges: what are we wrong about? What assumption in this ontology is incorrect? What entity category is missing? What if the relationship direction is reversed?"

**Phase 4 — Constraint Storm:**
> "Map the binding constraints on this network. What actually limits their operation? It's probably not the obvious thing."

**Phase 5 — Fragment Validation:**
Human analyst evaluates fragments against domain knowledge, HUMINT, and investigative intuition. Surviving fragments become:
- New investigation leads (fed back to OpenPlanter)
- New ontology categories (fed back to OpenPlanter's entity model)
- New questions (fed back to edge-finding)

---

## What This Builds That Doesn't Exist

### 1. The Unnamed Pattern Registry

Current intelligence tools can find connections within *named* categories. Person → Organization. Transaction → Account. Location → Event.

This system creates a registry of **unnamed patterns** — fragments that survived validation but don't fit existing ontology types. Over time, some of these coalesce into new named categories. The system literally discovers new types of intelligence relationships.

### 2. Multi-Model Associative Divergence Analysis

No one is systematically using the *differences* between LLM outputs as an intelligence signal. When GPT, Claude, and Qwen produce different low-probability associations for the same entity constellation, the divergence map is itself analytical gold. Each model's training distribution encodes different slices of the world's information.

### 3. The HUMINT-AI Elastic Tether

Current systems treat human analysts as either consumers of AI output or supervisors who approve/reject. The elastic tether model is different: the human and AI are *co-explorers* of the problem space. The analyst's "something feels wrong" intuition becomes a first-class input that redirects the AI's exploration, not just a filter on its output.

### 4. Bias Cartography

By running edge-finding across multiple models on the same data, you can begin to map where each model's biases *are*. Not to eliminate them, but to understand them — to know that Model A over-associates financial entities with geographic patterns, while Model B over-associates temporal patterns with organizational structures. This becomes a tool for choosing which model to deploy for which investigation type.

---

## Implementation Path

### Phase 1: Proof of Concept (Weeks 1-4)

- Deploy OpenPlanter in Docker with a sample OSINT dataset (e.g., public campaign finance + corporate registry data)
- Run standard entity resolution and evidence chain construction
- Export resolved entities to structured format
- Conduct manual edge-finding sessions in Claude using the ontology output as context
- Document which fragments lead to verifiable new connections

### Phase 2: Multi-Model Edge Sessions (Weeks 5-8)

- Configure OpenPlanter with multiple LLM backends
- Build a simple pipeline: ontology subset → edge-finding prompt → multi-model execution → fragment collection
- Develop fragment comparison tooling (which associations appear across models, which diverge)
- Have analysts evaluate fragment quality and signal-to-noise ratio

### Phase 3: Feedback Loop (Weeks 9-12)

- Build the feedback path: validated fragments → new ontology types → new OpenPlanter search patterns
- Create the Unnamed Pattern Registry
- Instrument the loop: track which edge fragments eventually become named patterns
- Measure: does the system find connections that structured analysis alone misses?

### Phase 4: Persistence & Governance (Weeks 13-16)

- Add Neo4j or equivalent graph store for persistent ontology beyond OpenPlanter sessions
- Build export pipeline: OpenPlanter entities/relationships → graph database → visualization (Gephi, Neo4j Browser)
- Add provenance tracking: every edge fragment linked to its source data, model, session, and human validator
- Add access controls: edge fragments may touch sensitive connection hypotheses
- Build simple web dashboard for the Unnamed Pattern Registry (or use a shared markdown repo)

---

## Risks & Dark Edges

Applying edge-finding to its own proposal:

1. **Noise amplification** — Scatter probability produces a lot of fragments. Without strong human judgment, this drowns analysts in false leads. Mitigation: strict fragment validation protocol, confidence scoring, and the 30-day observation window from BREADCRUMB-01.

2. **Confirmation bias via LLM** — LLMs are agreeable. They'll find connections you *want* to see. Mitigation: multi-model divergence analysis, mandatory dark edges phase, explicit "what are we wrong about?" prompts.

3. **Governance gap** — Edge fragments are hypotheses, not evidence. If treated as findings prematurely, they could drive harmful actions. Mitigation: clear classification (fragment vs. validated finding vs. evidence), audit trail, human-in-the-loop gate before any fragment becomes actionable.

4. **Model training data leakage** — LLM associations may surface connections from their training data that are not present in the investigation data. This is simultaneously the power and the risk. Mitigation: provenance tracking distinguishes "found in data" from "found in model associations."

5. **Ethical boundaries** — OSINT + HUMINT + AI-powered edge exploration is powerful. Power needs constraints. Clear use policies, oversight structures, and ethical review must be first-class concerns, not afterthoughts.

---

## The Binding Constraint

Applying constraint storm methodology:

- **Technical:** Both components exist and are open-source. Integration is engineering, not invention.
- **Data:** OSINT is abundant. HUMINT requires relationships and trust.
- **Governance:** Edge fragments need new classification and handling procedures.
- **Adoption:** Analysts trained in structured methods may resist "scatter probability."
- **Validation:** How do you measure whether edge-finding actually produces better intelligence outcomes?

**Binding constraint identified:** Validation. Without a way to measure whether the edge fragments improve analytical outcomes compared to structured analysis alone, the system cannot demonstrate its value.

**Loop-breaker:** Start with historical cases where the answer is already known. Run edge-finding on the data *as it existed before the connection was discovered.* Does the system surface fragments that point toward the known answer? If yes: evidence of value. If no: evidence that the methodology needs refinement before deployment.

---

## Summary

| Layer | Tool | Role | Produces |
|-------|------|------|----------|
| Collection | OpenPlanter | Recursive OSINT ingestion & entity resolution | Resolved entities, evidence chains |
| Structure | OpenPlanter Ontology + Neo4j | Entity-relationship model & graph persistence | Typed relationships, queryable graph |
| Exploration | Edge Bird | Low-probability space discovery | Fragments, inversions, unnamed patterns |
| Judgment | Human Analyst | Elastic tether holder, HUMINT source | Validation, direction, domain expertise |

**The system's unique capability:** It doesn't just find connections within known categories. It discovers *new categories of connection* by deliberately exploring the space that structured analysis ignores — and it does this by using the weights and biases of multiple LLMs as complementary instruments rather than flaws to eliminate.

*The flock expands from the edge, not the center.*

---

## Sources

- [OpenPlanter — GitHub](https://github.com/ShinMegamiBoson/OpenPlanter)
- [OpenPlanter: Community Edition of Palantir — MarkTechPost](https://www.marktechpost.com/2026/02/21/is-there-a-community-edition-of-palantir-meet-openplanter-an-open-source-recursive-ai-agent-for-your-micro-surveillance-use-cases/)
- [OpenPlanter: Open-Source AI for OSINT Surveillance — i10x.ai](https://i10x.ai/news/openplanter-open-source-ai-agent-osint)

---

*Generated: 2026-02-24*
*Status: PROPOSAL — Awaiting review and edge-finding session*
