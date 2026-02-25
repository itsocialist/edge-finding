"""Fragment extraction, storage, and comparison."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime

import yaml


@dataclass
class Fragment:
    id: str
    content: str
    source_model: str
    phase: str  # scatter, dark_edges, constraint_storm
    fragment_type: str = "unknown"  # association, inversion, category_gap, temporal, metaphor, constraint
    entity_refs: list[str] = field(default_factory=list)
    analyst_confidence: str = ""  # high, medium, low, intuition-only
    validation_status: str = "unvalidated"  # unvalidated, signal, plausible, noise, inversion
    notes: str = ""
    created: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "source_model": self.source_model,
            "phase": self.phase,
            "fragment_type": self.fragment_type,
            "entity_refs": self.entity_refs,
            "analyst_confidence": self.analyst_confidence,
            "validation_status": self.validation_status,
            "notes": self.notes,
            "created": self.created,
        }

    @classmethod
    def from_dict(cls, d: dict) -> Fragment:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


def extract_fragments(
    raw_text: str,
    source_model: str,
    phase: str,
    session_id: str,
) -> list[Fragment]:
    """Extract numbered fragments from model output.

    Expects output like:
        1. Fragment text here...
        2. Another fragment...
    """
    # Match patterns like "1." or "1)" or "1:" at start of line
    pattern = r"(?:^|\n)\s*(\d+)\s*[.):\-]\s*(.+?)(?=\n\s*\d+\s*[.):\-]|\Z)"
    matches = re.findall(pattern, raw_text, re.DOTALL)

    fragments = []
    for num, content in matches:
        content = content.strip()
        if not content:
            continue
        frag_id = f"{session_id}-{source_model}-{phase}-{num.zfill(2)}"
        fragments.append(
            Fragment(
                id=frag_id,
                content=content,
                source_model=source_model,
                phase=phase,
            )
        )

    # Fallback: if no numbered fragments found, split by double newlines
    if not fragments and raw_text.strip():
        paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
        for i, content in enumerate(paragraphs, 1):
            frag_id = f"{session_id}-{source_model}-{phase}-{str(i).zfill(2)}"
            fragments.append(
                Fragment(
                    id=frag_id,
                    content=content,
                    source_model=source_model,
                    phase=phase,
                )
            )

    return fragments


def save_fragments(fragments: list[Fragment], path) -> None:
    data = [f.to_dict() for f in fragments]
    with open(path, "w") as fh:
        yaml.dump(data, fh, default_flow_style=False, sort_keys=False)


def load_fragments(path) -> list[Fragment]:
    with open(path) as fh:
        data = yaml.safe_load(fh) or []
    return [Fragment.from_dict(d) for d in data]
