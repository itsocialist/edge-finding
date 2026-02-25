"""Context packet: load entity/relationship data for edge-finding sessions."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Entity:
    id: str
    name: str
    type: str  # person, org, location, asset, government, etc.
    attributes: dict = field(default_factory=dict)

    def summary(self) -> str:
        attrs = ", ".join(f"{k}: {v}" for k, v in self.attributes.items())
        base = f"{self.name} [{self.type}]"
        return f"{base} ({attrs})" if attrs else base


@dataclass
class Relationship:
    source: str  # entity id
    target: str  # entity id
    type: str  # employs, funds, contracts_with, etc.
    evidence: str = ""
    confidence: str = "confirmed"  # confirmed, probable, possible

    def summary(self, entities: dict[str, Entity]) -> str:
        src = entities.get(self.source, Entity(self.source, self.source, "?"))
        tgt = entities.get(self.target, Entity(self.target, self.target, "?"))
        line = f"{src.name} --[{self.type}]--> {tgt.name}"
        if self.evidence:
            line += f"  (evidence: {self.evidence})"
        return line


@dataclass
class ContextPacket:
    """Everything an edge-finding session needs as input."""

    entities: list[Entity] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    timeline: list[dict] = field(default_factory=list)  # [{date, event, entities}]
    gaps: list[str] = field(default_factory=list)
    humint_notes: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    @property
    def entity_map(self) -> dict[str, Entity]:
        return {e.id: e for e in self.entities}

    def render(self) -> str:
        """Render context packet as text for LLM consumption."""
        parts = []

        # Entities
        parts.append("ENTITIES:")
        by_type: dict[str, list[Entity]] = {}
        for e in self.entities:
            by_type.setdefault(e.type, []).append(e)
        for etype, elist in sorted(by_type.items()):
            parts.append(f"  {etype} ({len(elist)}):")
            for e in elist:
                parts.append(f"    - {e.summary()}")

        # Relationships
        parts.append(f"\nRELATIONSHIPS ({len(self.relationships)}):")
        emap = self.entity_map
        for r in self.relationships:
            parts.append(f"  - {r.summary(emap)}")

        # Timeline
        if self.timeline:
            parts.append("\nTIMELINE:")
            for event in self.timeline:
                date = event.get("date", "?")
                desc = event.get("event", "?")
                ents = event.get("entities", [])
                ent_str = f" [{', '.join(ents)}]" if ents else ""
                parts.append(f"  {date}: {desc}{ent_str}")

        # Gaps
        if self.gaps:
            parts.append("\nGAPS (what's missing or unexplained):")
            for gap in self.gaps:
                parts.append(f"  - {gap}")

        # HUMINT
        if self.humint_notes:
            parts.append("\nHUMINT NOTES (analyst observations):")
            for note in self.humint_notes:
                parts.append(f"  - {note}")

        return "\n".join(parts)

    def save(self, path: Path) -> None:
        data = {
            "entities": [
                {"id": e.id, "name": e.name, "type": e.type, "attributes": e.attributes}
                for e in self.entities
            ],
            "relationships": [
                {
                    "source": r.source,
                    "target": r.target,
                    "type": r.type,
                    "evidence": r.evidence,
                    "confidence": r.confidence,
                }
                for r in self.relationships
            ],
            "timeline": self.timeline,
            "gaps": self.gaps,
            "humint_notes": self.humint_notes,
            "metadata": self.metadata,
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    @classmethod
    def load(cls, path: Path) -> ContextPacket:
        with open(path) as f:
            if path.suffix == ".json":
                data = json.load(f)
            else:
                data = yaml.safe_load(f)

        entities = [
            Entity(
                id=e["id"],
                name=e["name"],
                type=e.get("type", "unknown"),
                attributes=e.get("attributes", {}),
            )
            for e in data.get("entities", [])
        ]
        relationships = [
            Relationship(
                source=r["source"],
                target=r["target"],
                type=r.get("type", "related_to"),
                evidence=r.get("evidence", ""),
                confidence=r.get("confidence", "confirmed"),
            )
            for r in data.get("relationships", [])
        ]
        return cls(
            entities=entities,
            relationships=relationships,
            timeline=data.get("timeline", []),
            gaps=data.get("gaps", []),
            humint_notes=data.get("humint_notes", []),
            metadata=data.get("metadata", {}),
        )
