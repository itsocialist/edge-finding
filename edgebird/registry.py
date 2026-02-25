"""Unnamed Pattern Registry: track edge fragments awaiting names."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import yaml

REGISTRY_DIR = Path("registry")

VALID_STATUSES = {"active", "watching", "named", "promoted", "merged", "archived"}


@dataclass
class UnnamedPattern:
    pattern_id: str
    discovered: str
    source_session: str
    source_models: list[str]
    convergence: str  # convergent, unique, contradictory
    description: str
    entity_refs: list[str] = field(default_factory=list)
    fragment_ids: list[str] = field(default_factory=list)
    analyst_notes: str = ""
    validation_status: str = "untested"  # untested, testable, tested_positive, tested_negative
    validation_method: str = ""
    related_patterns: list[str] = field(default_factory=list)
    status: str = "active"
    named_as: str | None = None
    promoted_to: str | None = None

    def to_dict(self) -> dict:
        return {
            "pattern_id": self.pattern_id,
            "discovered": self.discovered,
            "source_session": self.source_session,
            "source_models": self.source_models,
            "convergence": self.convergence,
            "description": self.description,
            "entity_refs": self.entity_refs,
            "fragment_ids": self.fragment_ids,
            "analyst_notes": self.analyst_notes,
            "validation_status": self.validation_status,
            "validation_method": self.validation_method,
            "related_patterns": self.related_patterns,
            "status": self.status,
            "named_as": self.named_as,
            "promoted_to": self.promoted_to,
        }

    @classmethod
    def from_dict(cls, d: dict) -> UnnamedPattern:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


class Registry:
    """File-backed Unnamed Pattern Registry."""

    def __init__(self, registry_dir: Path | None = None):
        self.dir = registry_dir or REGISTRY_DIR
        self.dir.mkdir(parents=True, exist_ok=True)
        self._index_path = self.dir / "index.yaml"

    def _load_index(self) -> list[dict]:
        if not self._index_path.exists():
            return []
        with open(self._index_path) as f:
            return yaml.safe_load(f) or []

    def _save_index(self, entries: list[dict]) -> None:
        with open(self._index_path, "w") as f:
            yaml.dump(entries, f, default_flow_style=False, sort_keys=False)

    def _next_id(self) -> str:
        entries = self._load_index()
        if not entries:
            return "UNP-001"
        max_num = 0
        for e in entries:
            pid = e.get("pattern_id", "")
            if pid.startswith("UNP-"):
                try:
                    num = int(pid.split("-")[1])
                    max_num = max(max_num, num)
                except ValueError:
                    pass
        return f"UNP-{max_num + 1:03d}"

    def add(self, pattern: UnnamedPattern) -> UnnamedPattern:
        """Add a new unnamed pattern to the registry."""
        if not pattern.pattern_id:
            pattern.pattern_id = self._next_id()
        if not pattern.discovered:
            pattern.discovered = datetime.now().strftime("%Y-%m-%d")

        entries = self._load_index()
        entries.append(pattern.to_dict())
        self._save_index(entries)
        return pattern

    def list_all(self, status: str | None = None) -> list[UnnamedPattern]:
        """List all patterns, optionally filtered by status."""
        entries = self._load_index()
        patterns = [UnnamedPattern.from_dict(e) for e in entries]
        if status:
            patterns = [p for p in patterns if p.status == status]
        return patterns

    def get(self, pattern_id: str) -> UnnamedPattern | None:
        """Get a specific pattern by ID."""
        entries = self._load_index()
        for e in entries:
            if e.get("pattern_id") == pattern_id:
                return UnnamedPattern.from_dict(e)
        return None

    def update_status(self, pattern_id: str, new_status: str) -> bool:
        """Update a pattern's status."""
        if new_status not in VALID_STATUSES:
            return False
        entries = self._load_index()
        for e in entries:
            if e.get("pattern_id") == pattern_id:
                e["status"] = new_status
                self._save_index(entries)
                return True
        return False

    def update_notes(self, pattern_id: str, notes: str) -> bool:
        """Append analyst notes to a pattern."""
        entries = self._load_index()
        for e in entries:
            if e.get("pattern_id") == pattern_id:
                existing = e.get("analyst_notes", "")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                if existing:
                    e["analyst_notes"] = f"{existing}\n\n[{timestamp}] {notes}"
                else:
                    e["analyst_notes"] = f"[{timestamp}] {notes}"
                self._save_index(entries)
                return True
        return False

    def name_pattern(self, pattern_id: str, name: str) -> bool:
        """Promote an unnamed pattern to a named type."""
        entries = self._load_index()
        for e in entries:
            if e.get("pattern_id") == pattern_id:
                e["status"] = "named"
                e["named_as"] = name
                self._save_index(entries)
                return True
        return False

    def stats(self) -> dict:
        """Return registry statistics."""
        entries = self._load_index()
        by_status: dict[str, int] = {}
        for e in entries:
            s = e.get("status", "unknown")
            by_status[s] = by_status.get(s, 0) + 1
        return {
            "total": len(entries),
            "by_status": by_status,
        }
