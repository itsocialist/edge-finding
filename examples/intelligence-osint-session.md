# Worked Example: Intelligence Edge-Finding Session

**Session type:** OSINT network analysis with edge exploration
**Scenario:** Government procurement pattern investigation (synthetic data)
**Purpose:** Demonstrate the three-layer system in action

---

## The Setup

### The Structured Analysis (Layers 1 & 2)

OpenPlanter ingested three public datasets:
- Government contract awards (2023-2025)
- Corporate registry filings
- Lobbying disclosure records

Standard entity resolution produced **23 entities** and **47 known relationships**. Palantir-style ontology modeled them as:

```
ENTITIES:
  Persons:       8 individuals (named officers, lobbyists, officials)
  Organizations: 11 companies (primes, subs, consultancies)
  Government:    3 agencies
  Assets:        1 facility

RELATIONSHIPS:
  employs:           12
  contracts_with:    8
  lobbied_by:        6
  subcontracts_to:   5
  shares_address:    4
  formerly_employed: 3
  registered_agent:  3
  co_filed:          2
  shares_officer:    4
```

### The Gaps

Structured analysis flagged three anomalies it couldn't resolve:

1. **Subcontractor Delta LLC** was registered 23 days before receiving a $4.2M subcontract. No prior contracting history. No web presence. Single registered agent.

2. **Lobbyist C** disclosed 11 meetings with Agency-2 in Q3 2024, then zero contact in Q4. The contract was awarded in Q1 2025. Normal pattern would show continued contact through award.

3. **Entity-7** (a mid-size consulting firm) appears in all three datasets but always peripherally — never as the prime, never as the lobbyist, never as the awardee. Yet it shares addresses or officers with 6 of the 23 entities.

Standard analysis concluded: "likely coordination, insufficient evidence for specific mechanism."

### The HUMINT

An analyst with domain expertise noted:

> "Entity-7 feels like the center of something but the data makes it look like the periphery. I've seen this pattern before but I can't articulate what 'this pattern' is."

This is exactly the kind of input that edge-finding is designed to work with. The analyst has a signal they can't name.

---

## The Edge-Finding Session (Layer 3)

### Phase 1: Scatter

Context packet loaded. Scatter prompt sent to three models independently.

**Claude fragments:**

> F-01: "Delta LLC's 23-day registration-to-award gap isn't a red flag — it's a signature. The entity was purpose-built. The question isn't who owns Delta, it's who *designed* the requirement that only Delta could fulfill."

> F-02: "Entity-7's peripheral presence across all three datasets is topologically central. It's not on the periphery — it's the connective tissue. Remove Entity-7 and the network fragments into three disconnected clusters."

> F-03: "Lobbyist C's silence in Q4 isn't absence of activity. It's a mode switch. The lobbying phase ended because the decision was already made. Q4 was execution, not persuasion."

**GPT fragments:**

> F-04: "Entity-7's registered agent, M. Torres, dissolved a previous entity 18 months before Delta LLC was created. The dissolved entity held a similar facility clearance. Asset transfer without paper trail — clearance follows people, not entities."

> F-05: "The timing: lobbying stops → contract spec finalized → Delta registered → subcontract awarded. This isn't corruption — it's a procurement pipeline. Each phase has a different visible actor so no single entity appears across all phases."

> F-06: "Three of Entity-7's shared-officer relationships connect to entities in different sectors. Cross-sector officer overlap at this density suggests a holding structure that doesn't appear in the corporate registry."

**Qwen fragments:**

> F-07: "The 47-52 day transaction rhythm across Entity-3, Entity-7, and Delta LLC doesn't match any regulatory cycle. It matches a human decision cadence — approximately weekly meeting of a 7-person group with rotating quorum."

> F-08: "Entity-7's role maps to what Chinese corporate governance calls a 'shadow coordinator' — an entity that never appears as principal but controls information flow between entities that officially have no relationship."

> F-09: "The dissolved entity (from 18 months prior) and Delta LLC share no legal connection. But their document filing patterns — formatting, timing, section ordering — suggest the same preparer."

---

### Phase 2: Cross-Model Divergence

| Fragment | Claude | GPT | Qwen | Pattern |
|----------|--------|-----|------|---------|
| Purpose-built entity (Delta) | F-01 | F-05 | - | Convergent (2/3) — both see Delta as designed |
| Entity-7 as hidden center | F-02 | F-06 | F-08 | **Convergent (3/3)** — strongest signal |
| Lobbyist silence = mode switch | F-03 | F-05 | - | Convergent (2/3) — phased operation |
| Dissolved entity connection | - | F-04 | F-09 | Convergent (2/3) — different evidence, same link |
| Transaction rhythm | - | - | F-07 | Unique to Qwen — meeting cadence hypothesis |
| Shadow coordinator concept | - | - | F-08 | Unique to Qwen — cultural pattern recognition |
| Document preparer signature | - | - | F-09 | Unique to Qwen — forensic detail |

**Key finding:** All three models converge on Entity-7 as the functional center of the network despite appearing peripheral in structured data. This is the strongest signal in the session.

**Qwen unique fragments:** The meeting cadence (F-07), shadow coordinator concept (F-08), and document preparer pattern (F-09) are all unique to Qwen. Two possible explanations:
1. Qwen's training data includes different governance/forensic patterns (likely — different cultural and linguistic training distribution)
2. Qwen is constructing narratives from noise (possible but less likely given the specificity)

Analyst judgment needed.

---

### Phase 3: Dark Edges

> "Dark edges: what are we wrong about? What assumption in this entity model is incorrect?"

**Dark edge responses (composite):**

D-01: "You're assuming the 23 entities are the complete network. Entity-7's connectivity pattern suggests at least 2-3 additional entities that don't appear in any of the three datasets. The network is larger than your data."

D-02: "You're assuming the government agencies are passive recipients of lobbying. What if Agency-2 is an active participant — not captured but capturing? The contract spec may have been co-designed."

D-03: "You're assuming the timeline is linear: lobby → spec → register → award. What if some of these happened in parallel? The lobbying may have been cover activity for a decision already in motion."

D-04: "You're assuming Entity-7 is the coordinator. Alternative: Entity-7 is the *artifact* of coordination — a shared services structure that exists because the actual coordinators needed a common entity for logistics. The coordinator might be a person who doesn't appear as an officer of Entity-7."

---

### Phase 4: Constraint Storm

> "Map the binding constraints on this network. What actually limits their operation?"

**Constraints identified:**

| Constraint | Type | Binding? |
|------------|------|----------|
| Facility clearance required | Structural | No — can be transferred via personnel |
| Contract dollar threshold triggers additional review | Regulatory | No — subcontracting keeps amounts below threshold |
| Officer disclosure requirements | Legal | **Possibly** — shared officers are visible |
| Registration timing leaves paper trail | Temporal | No — 23-day gap is legal |
| Lobbyist disclosure is public | Transparency | No — they simply stop lobbying before the sensitive phase |
| Personnel overlap is detectable | Analytical | **Yes — this is the binding constraint** |

**Binding constraint:** Personnel overlap. The network can hide entity relationships, phase its activity to avoid visibility, and structure transactions below review thresholds. But it cannot eliminate the *people* who connect the entities. The same individuals must appear across multiple entities because their expertise and clearances are the scarce resource.

**Implication:** Focus investigation on personnel, not entities. The entity structure is designed to be opaque. The personnel connections are the constraint they cannot eliminate.

---

### Phase 5: Fragment Validation & Routing

Analyst evaluation:

| Fragment | Validation | Routing |
|----------|-----------|---------|
| Entity-7 as hidden center (F-02, F-06, F-08) | **Validated** — consistent with HUMINT ("feels like center") | OpenPlanter: run Entity-7-centered network analysis |
| Purpose-built Delta (F-01, F-05) | **Testable** — check contract spec authorship metadata | OpenPlanter: FOIA request for spec development records |
| Dissolved entity link (F-04, F-09) | **Testable** — compare document formatting signatures | New search pattern: dissolved entities sharing preparers |
| Transaction rhythm (F-07) | **Testable** — pull full transaction timeline | OpenPlanter: periodic pattern analysis |
| Shadow coordinator (F-08) | **Speculative** — useful frame, not directly testable | Next edge-finding session as context |
| Agency co-design (D-02) | **Dark edge** — would change everything if true | Flag for senior analyst review |

### Unnamed Pattern Registry Entries

Two fragments entered the registry:

**UNP-001: Temporal Breathing Pattern** — The 47-52 day cycle. Not an event, not a calendar pattern. A network rhythm suggesting hidden coordination cadence.

**UNP-002: Peripheral Centrality** — An entity that appears at the edge of every dataset but is topologically central when the datasets are fused. Designed to appear unimportant. This may be a generalizable pattern type.

---

## What the Three Layers Produced Together

**OpenPlanter alone** found: 23 entities, 47 relationships, 3 anomalies, and "likely coordination, insufficient evidence."

**Adding the ontology layer** structured this into queryable, governed data with typed relationships and audit trail.

**Adding edge-finding** produced:
- A reframing of Entity-7 from peripheral to central (validated by 3/3 models and HUMINT)
- A binding constraint (personnel overlap) that redirects the investigation's focus
- Two new pattern types for the registry (temporal breathing, peripheral centrality)
- Three testable hypotheses not present in structured analysis
- A dark edge (agency co-design) that could change the entire investigation frame

**The structured analysis told us *what* the data contains.**
**Edge-finding told us *what the data is trying not to show*.**

---

## Caveats

This is a **synthetic scenario** built to demonstrate the methodology. Real investigations involve:
- Messier data with more noise
- Legal and ethical constraints on collection
- Adversaries who actively counter-investigate
- Institutional politics around unconventional analytical methods
- Stakes that make false positives genuinely dangerous

The methodology must be validated on real historical cases (where the answer is already known) before deployment on active investigations. See the binding constraint analysis in `RESEARCH-INTELLIGENCE-INTEGRATION.md`.

---

*Standard analysis finds what the data contains. Edge-finding finds what the data is trying to hide.*
