"""Scatter engine: generate edge-finding prompts and execute across models."""

from __future__ import annotations

from edgebird.context import ContextPacket
from edgebird.models import ModelResponse, scatter_multi_sync

SYSTEM_PROMPT = """\
You are an edge-finding agent for investigative research. Your task is to \
explore low-probability connection space — the unlikely associations, unnamed \
patterns, and hidden relationships that structured analysis misses.

Rules:
- Do NOT give expected, safe, center-of-distribution answers.
- Scatter probability. Range to the edges.
- Report fragments: partial patterns, inversions, category gaps, temporal \
anomalies, things that "remind you of" something you can't quite name.
- Do not explain or justify. Just report what you find.
- Number each fragment. Produce exactly {count} fragments.
- Each fragment should be 1-3 sentences.
- Prioritize diversity over coherence.
"""

SCATTER_PROMPT = """\
Edge bird: I'm going to share an entity network from an OSINT investigation. \
Your task is to scatter probability — explore the unlikely connection space.

{context}

---

What unlikely connections might exist that haven't been named? What entity \
categories might be missing from this model entirely? What relationship types \
don't have names yet? What if the direction of influence is reversed?

What's at the edges?
"""

DARK_EDGES_PROMPT = """\
Dark edges on this investigation. What are we wrong about? Which of our known \
relationships might be misclassified? Which entity is likely misidentified or \
playing a different role than assigned? What assumption in our entity model is \
most likely incorrect?

{context}

---

Don't soften. Name the assumption and name the alternative. Be specific. \
The dark edges are where the real risks live. Report exactly {count} dark edges, \
numbered.
"""

CONSTRAINT_STORM_PROMPT = """\
Constraint storm: map the binding constraints on this network.

{context}

---

If these entities are operating together toward some objective, what actually \
limits their operation? Think about: information constraints, resource constraints, \
temporal constraints, geographic constraints, regulatory constraints, trust \
constraints.

The binding constraint is usually not the obvious one. Find it.

Report exactly {count} constraints, numbered, then identify which one is the \
binding constraint and explain why.
"""


def build_scatter_prompt(ctx: ContextPacket) -> str:
    return SCATTER_PROMPT.format(context=ctx.render())


def build_dark_edges_prompt(ctx: ContextPacket, count: int = 8) -> str:
    return DARK_EDGES_PROMPT.format(context=ctx.render(), count=count)


def build_constraint_storm_prompt(ctx: ContextPacket, count: int = 8) -> str:
    return CONSTRAINT_STORM_PROMPT.format(context=ctx.render(), count=count)


def run_scatter(
    ctx: ContextPacket,
    models: list[dict] | None = None,
    fragment_count: int = 10,
    temperature: float = 1.0,
) -> list[ModelResponse]:
    """Run scatter phase across multiple models."""
    system = SYSTEM_PROMPT.format(count=fragment_count)
    user = build_scatter_prompt(ctx)
    return scatter_multi_sync(
        system_prompt=system,
        user_prompt=user,
        models=models,
        temperature=temperature,
    )


def run_dark_edges(
    ctx: ContextPacket,
    models: list[dict] | None = None,
    count: int = 8,
    temperature: float = 1.0,
) -> list[ModelResponse]:
    """Run dark edges phase across multiple models."""
    system = SYSTEM_PROMPT.format(count=count)
    user = build_dark_edges_prompt(ctx, count=count)
    return scatter_multi_sync(
        system_prompt=system,
        user_prompt=user,
        models=models,
        temperature=temperature,
    )


def run_constraint_storm(
    ctx: ContextPacket,
    models: list[dict] | None = None,
    count: int = 8,
    temperature: float = 1.0,
) -> list[ModelResponse]:
    """Run constraint storm phase across multiple models."""
    system = SYSTEM_PROMPT.format(count=count)
    user = build_constraint_storm_prompt(ctx, count=count)
    return scatter_multi_sync(
        system_prompt=system,
        user_prompt=user,
        models=models,
        temperature=temperature,
    )
