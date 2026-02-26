"""Dataclass schemas for Person and Company entities."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Person:
    name: str
    linkedin_url: Optional[str] = None
    github_username: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    seniority: Optional[str] = None
    signals: list[str] = field(default_factory=list)
    source_urls: list[str] = field(default_factory=list)
    date_captured: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    webset_id: Optional[int] = None

    def natural_key(self) -> Optional[str]:
        """Return a deduplication key: linkedin_url or github_username."""
        return self.linkedin_url or self.github_username

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json_str(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict) -> Person:
        if isinstance(data.get("signals"), str):
            data["signals"] = json.loads(data["signals"])
        if isinstance(data.get("source_urls"), str):
            data["source_urls"] = json.loads(data["source_urls"])
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in known})


@dataclass
class Company:
    name: str
    domain: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    size_range: Optional[str] = None
    tech_signals: list[str] = field(default_factory=list)
    source_urls: list[str] = field(default_factory=list)
    date_captured: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    webset_id: Optional[int] = None

    def natural_key(self) -> Optional[str]:
        """Return a deduplication key: domain."""
        return self.domain

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json_str(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict) -> Company:
        if isinstance(data.get("tech_signals"), str):
            data["tech_signals"] = json.loads(data["tech_signals"])
        if isinstance(data.get("source_urls"), str):
            data["source_urls"] = json.loads(data["source_urls"])
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in known})
