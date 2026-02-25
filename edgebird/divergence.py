"""Divergence analysis: compare fragments across models."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from edgebird.fragments import Fragment
from edgebird.models import ModelResponse, scatter_multi_sync

SIMILARITY_SYSTEM = """\
You are an analytical assistant comparing investigative fragments. You will \
receive fragments from different AI models analyzing the same entity network. \
Your job is to identify which fragments are touching the same underlying pattern, \
even if they describe it differently.

Respond with a JSON array of groups. Each group is an object with:
- "theme": a short label for the shared pattern (3-8 words)
- "fragments": list of fragment IDs that touch this theme
- "convergence": "convergent" if multiple models agree, "unique" if only one model, \
  "contradictory" if models disagree about direction or interpretation
- "signal_note": one sentence about why this convergence/divergence matters

Also include a final group for any fragments that don't fit any theme, with \
theme "ungrouped".
"""


@dataclass
class DivergenceGroup:
    theme: str
    fragment_ids: list[str]
    models: list[str]
    convergence: str  # convergent, unique, contradictory
    signal_note: str = ""


@dataclass
class DivergenceMap:
    groups: list[DivergenceGroup] = field(default_factory=list)
    total_fragments: int = 0
    models_used: list[str] = field(default_factory=list)

    @property
    def convergent(self) -> list[DivergenceGroup]:
        return [g for g in self.groups if g.convergence == "convergent"]

    @property
    def unique(self) -> list[DivergenceGroup]:
        return [g for g in self.groups if g.convergence == "unique"]

    @property
    def contradictory(self) -> list[DivergenceGroup]:
        return [g for g in self.groups if g.convergence == "contradictory"]


def build_divergence_prompt(fragments: list[Fragment]) -> str:
    """Build prompt for LLM-assisted divergence analysis."""
    parts = ["Fragments from multiple models analyzing the same entity network:\n"]

    by_model: dict[str, list[Fragment]] = defaultdict(list)
    for f in fragments:
        by_model[f.source_model].append(f)

    for model, frags in sorted(by_model.items()):
        parts.append(f"### Model: {model}")
        for f in frags:
            parts.append(f"[{f.id}] {f.content}")
        parts.append("")

    parts.append("Group these fragments by shared underlying pattern or theme.")
    parts.append("Identify convergent, unique, and contradictory patterns.")
    return "\n".join(parts)


def analyze_divergence_simple(fragments: list[Fragment]) -> DivergenceMap:
    """Simple rule-based divergence analysis (no LLM needed).

    Groups fragments by model and identifies basic patterns:
    - Fragments from a single model -> unique
    - Multiple fragments sharing keywords -> possibly convergent
    """
    models_used = sorted(set(f.source_model for f in fragments))

    # Group by model
    by_model: dict[str, list[Fragment]] = defaultdict(list)
    for f in fragments:
        by_model[f.source_model].append(f)

    groups = []
    for model, frags in sorted(by_model.items()):
        for f in frags:
            groups.append(
                DivergenceGroup(
                    theme=f"Fragment from {model}",
                    fragment_ids=[f.id],
                    models=[model],
                    convergence="unique",
                    signal_note=f"Single-model fragment. Requires analyst evaluation.",
                )
            )

    return DivergenceMap(
        groups=groups,
        total_fragments=len(fragments),
        models_used=models_used,
    )


def analyze_divergence_llm(
    fragments: list[Fragment],
    analysis_model: dict | None = None,
) -> tuple[DivergenceMap, str]:
    """LLM-assisted divergence analysis.

    Uses a model to compare fragments across models and identify
    convergent, unique, and contradictory patterns.

    Returns the DivergenceMap and raw LLM analysis text.
    """
    if not analysis_model:
        analysis_model = {"id": "anthropic/claude-sonnet-4-20250514", "label": "analyst"}

    prompt = build_divergence_prompt(fragments)
    responses = scatter_multi_sync(
        system_prompt=SIMILARITY_SYSTEM,
        user_prompt=prompt,
        models=[analysis_model],
        temperature=0.3,
    )

    raw_analysis = responses[0].content if responses else ""

    # Return raw analysis — structured parsing is fragile with LLM JSON.
    # The CLI displays the raw analysis for human interpretation.
    models_used = sorted(set(f.source_model for f in fragments))
    return (
        DivergenceMap(
            groups=[],
            total_fragments=len(fragments),
            models_used=models_used,
        ),
        raw_analysis,
    )


def render_fragment_matrix(fragments: list[Fragment]) -> str:
    """Render a text-based fragment matrix for terminal display."""
    models = sorted(set(f.source_model for f in fragments))
    by_model: dict[str, list[Fragment]] = defaultdict(list)
    for f in fragments:
        by_model[f.source_model].append(f)

    lines = []
    max_model_len = max(len(m) for m in models) if models else 10

    # Header
    header = f"{'#':<4} {'Fragment (truncated)':<60}"
    for m in models:
        header += f" {m:<{max_model_len}}"
    lines.append(header)
    lines.append("-" * len(header))

    # One row per fragment
    for i, f in enumerate(fragments, 1):
        content_short = f.content[:57] + "..." if len(f.content) > 60 else f.content
        content_short = content_short.replace("\n", " ")
        row = f"{i:<4} {content_short:<60}"
        for m in models:
            if f.source_model == m:
                row += f" {'X':<{max_model_len}}"
            else:
                row += f" {'-':<{max_model_len}}"
        lines.append(row)

    return "\n".join(lines)
