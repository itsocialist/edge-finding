# Unnamed Pattern Registry

**Purpose:** Track edge fragments that survived validation but don't fit existing ontology categories
**Status:** Living document — patterns may be promoted, merged, archived, or named
**Core principle:** If it doesn't have a name, the system can't search for it. This registry holds patterns until they earn names.

---

## Why This Exists

Structured intelligence analysis operates through named categories: Person, Organization, Transaction, Location, Event, Communication, Asset. Relationships are typed: owns, employs, contacted, traveled-to, funded.

Edge-finding sessions produce fragments that don't fit these categories. A temporal rhythm that isn't an "event." A relationship that isn't "employment" or "ownership" but something else. An entity that isn't a person or organization but some emergent structure.

These fragments die in structured systems because there's no field to put them in. The Unnamed Pattern Registry keeps them alive until they either:

1. **Get named** — enough instances accumulate that the pattern becomes recognizable and deserves an ontology type
2. **Get merged** — two unnamed patterns turn out to be the same thing seen from different angles
3. **Get archived** — after sufficient time and testing, the pattern appears to be noise
4. **Get promoted** — the pattern is validated and becomes a formal investigation lead

---

## Registry Structure

### Entry Format

```yaml
pattern_id: UNP-001
discovered: 2026-02-24
source_session: [session reference]
source_models: [which LLMs surfaced this]
convergence: convergent | unique | contradictory

description: |
  Plain language description of what was observed.
  Not what it "means" — just what the pattern looks like.

entity_refs:
  - [entities from the investigation that this touches]

fragment_evidence:
  - fragment_id: scatter-XXX
    model: [source]
    content: [the actual fragment text]

analyst_notes: |
  What the human analyst observed about this pattern.
  Domain context. Gut feeling. HUMINT connections.

validation_status: untested | testable | tested_positive | tested_negative | inconclusive
validation_method: |
  How would you test whether this pattern is real?
  What evidence would confirm or deny it?

related_patterns:
  - [other UNP entries that may be connected]

status: active | watching | archived | named | promoted
named_as: null  # filled when pattern gets a name
promoted_to: null  # filled when pattern becomes formal lead
```

---

## Lifecycle

```
DISCOVERED → ACTIVE → WATCHING → [OUTCOME]

Outcomes:
  NAMED:     Pattern accumulated enough instances to get an ontology type
  PROMOTED:  Pattern validated and became a formal investigation lead
  MERGED:    Combined with another UNP entry (same pattern, different angles)
  ARCHIVED:  Tested negative or insufficient evidence after observation period
```

### Status Definitions

**Active:** Recently discovered, not yet tested. Under active consideration.

**Watching:** Initial assessment complete. Not enough evidence to promote or archive. Waiting for new data, new edge-finding sessions, or HUMINT input.

**Named:** The pattern has been seen enough times, across enough investigations, that it deserves a formal ontology type. Document the new type definition and feed it back to the ontology layer.

**Promoted:** This specific pattern instance has been validated in its specific investigation context. It becomes a formal lead. Routing: back to OpenPlanter for targeted search, or to the analyst team for action.

**Merged:** This pattern and another UNP entry are the same thing observed from different angles or by different models. Combine them. The merge itself is informative — it means multiple paths converged on the same unnamed structure.

**Archived:** After testing or observation period (minimum 30 days), the pattern appears to be noise. Archive, don't delete — noise can become signal when new context arrives.

---

## Example Entries

### UNP-001: Temporal Breathing Pattern

```yaml
pattern_id: UNP-001
discovered: 2026-02-24
source_session: intelligence-session-001
source_models: [Claude, Qwen]
convergence: convergent

description: |
  Multiple entities in the network show a synchronized activity rhythm
  that doesn't map to any business calendar, regulatory deadline, or
  seasonal pattern. Activity clusters at irregular but repeating intervals
  of approximately 47-52 days. Not an event — more like a "breathing"
  pattern in the network's transaction frequency.

entity_refs: [Entity-3, Entity-7, Entity-12, Entity-15]

fragment_evidence:
  - fragment_id: scatter-017
    model: Claude
    content: "The transaction timing doesn't follow calendar logic. It follows
              something internal — like a resource cycle or a decision loop
              with a roughly 7-week period."
  - fragment_id: scatter-023
    model: Qwen
    content: "Similar periodicity observed in networks managing rotating
              resource pools — the cycle length suggests a human decision
              chain of 3-4 people with sequential approval."

analyst_notes: |
  HUMINT suggests Entity-3 has a reporting relationship to someone
  not in our entity model. The 47-52 day cycle could be a meeting
  cadence. Worth checking travel records for Entity-3 at these intervals.

validation_status: testable
validation_method: |
  Pull Entity-3 travel records and communication metadata.
  Check for periodic patterns aligning with the 47-52 day cycle.
  If pattern holds: evidence of an unmodeled relationship/entity.

related_patterns: []
status: active
named_as: null
promoted_to: null
```

### UNP-002: Inverse Authority Flow

```yaml
pattern_id: UNP-002
discovered: 2026-02-24
source_session: intelligence-session-001
source_models: [GPT]
convergence: unique

description: |
  The formal organizational hierarchy says Entity-5 reports to Entity-2.
  But transaction patterns, communication timing, and resource allocation
  suggest information and authority flow in the opposite direction.
  Entity-5 acts before Entity-2 authorizes. Entity-2's "decisions"
  consistently align with Entity-5's prior resource movements.

entity_refs: [Entity-2, Entity-5]

fragment_evidence:
  - fragment_id: scatter-031
    model: GPT
    content: "Entity-2 is the named principal but Entity-5 is the functional
              one. The paper trail shows authorization flowing down but the
              actual decision signatures flow up. Look at who moves money
              before the meeting versus after."

analyst_notes: |
  Only GPT surfaced this. Could be narrative over-fitting (known GPT bias).
  But field reports have noted that Entity-5 seems "unusually well-informed"
  for their stated role. Worth a closer look.

validation_status: testable
validation_method: |
  Timeline analysis: do Entity-5's financial movements consistently
  precede Entity-2's formal authorizations? If yes, the authority
  flow is inverted from what the org chart shows.

related_patterns: [UNP-001]  # timing pattern may connect
status: active
named_as: null
promoted_to: null
```

---

## Pattern Naming Ceremony

When an unnamed pattern accumulates enough evidence to deserve a name:

1. **Document the instances** — how many times, across how many investigations, has this pattern appeared?
2. **Describe the type** — what are the defining characteristics? What makes this pattern different from existing ontology types?
3. **Define the schema** — what properties does this new entity/relationship type need?
4. **Name it** — use analyst language, not academic language. The name should be immediately recognizable to practitioners.
5. **Feed back** — add the new type to the ontology. Configure OpenPlanter to recognize and search for it going forward.

**Example:** If "Temporal Breathing Pattern" (UNP-001) is validated and found in 3+ investigations, it might become a named relationship type: **Synchronized Cycle** — a non-calendrical periodic correlation between entity activities suggesting hidden coordination.

The system just learned to see something it couldn't see before.

---

## Registry Maintenance

- **Review active entries monthly** — has new evidence arrived?
- **Archive after 90 days** if no new evidence and untestable
- **Never delete** — archive only. Today's noise is tomorrow's context.
- **Cross-reference new entries** against all existing entries. Merges are high-value events.
- **Track naming rate** — how many UNP entries eventually get named? This is a measure of the system's pattern discovery efficiency.

---

*What we can't name, we can't search for. What we register, we can eventually find.*
