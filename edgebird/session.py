"""Session management: lifecycle, logging, persistence."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import yaml

from edgebird.context import ContextPacket
from edgebird.fragments import Fragment

SESSIONS_DIR = Path("sessions")


@dataclass
class Session:
    session_id: str
    created: str
    domain: str = ""
    analyst: str = ""
    models_used: list[str] = field(default_factory=list)
    context_path: str = ""
    entity_count: int = 0
    relationship_count: int = 0
    phases_completed: list[str] = field(default_factory=list)
    fragment_count: int = 0
    fragments_validated: int = 0
    leads_generated: int = 0
    patterns_registered: int = 0
    notes: str = ""
    status: str = "active"  # active, completed, abandoned

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "created": self.created,
            "domain": self.domain,
            "analyst": self.analyst,
            "models_used": self.models_used,
            "context_path": self.context_path,
            "entity_count": self.entity_count,
            "relationship_count": self.relationship_count,
            "phases_completed": self.phases_completed,
            "fragment_count": self.fragment_count,
            "fragments_validated": self.fragments_validated,
            "leads_generated": self.leads_generated,
            "patterns_registered": self.patterns_registered,
            "notes": self.notes,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, d: dict) -> Session:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


class SessionManager:
    """Manage edge-finding investigation sessions."""

    def __init__(self, sessions_dir: Path | None = None):
        self.dir = sessions_dir or SESSIONS_DIR
        self.dir.mkdir(parents=True, exist_ok=True)

    def _session_dir(self, session_id: str) -> Path:
        return self.dir / session_id

    def _session_meta(self, session_id: str) -> Path:
        return self._session_dir(session_id) / "session.yaml"

    def _fragments_path(self, session_id: str, phase: str) -> Path:
        return self._session_dir(session_id) / f"fragments-{phase}.yaml"

    def _raw_path(self, session_id: str, phase: str, model: str) -> Path:
        return self._session_dir(session_id) / f"raw-{phase}-{model}.md"

    def create(
        self,
        ctx: ContextPacket,
        domain: str = "",
        analyst: str = "",
        context_path: str = "",
    ) -> Session:
        """Create a new session."""
        now = datetime.now()
        session_id = now.strftime("session-%Y%m%d-%H%M%S")
        session = Session(
            session_id=session_id,
            created=now.isoformat(),
            domain=domain,
            analyst=analyst,
            context_path=context_path,
            entity_count=len(ctx.entities),
            relationship_count=len(ctx.relationships),
        )

        sdir = self._session_dir(session_id)
        sdir.mkdir(parents=True, exist_ok=True)

        # Save session metadata
        with open(self._session_meta(session_id), "w") as f:
            yaml.dump(session.to_dict(), f, default_flow_style=False, sort_keys=False)

        # Save rendered context
        with open(sdir / "context.txt", "w") as f:
            f.write(ctx.render())

        return session

    def load(self, session_id: str) -> Session | None:
        meta = self._session_meta(session_id)
        if not meta.exists():
            return None
        with open(meta) as f:
            data = yaml.safe_load(f)
        return Session.from_dict(data)

    def update(self, session: Session) -> None:
        with open(self._session_meta(session.session_id), "w") as f:
            yaml.dump(session.to_dict(), f, default_flow_style=False, sort_keys=False)

    def save_raw_output(self, session_id: str, phase: str, model: str, content: str) -> None:
        """Save raw model output for a phase."""
        path = self._raw_path(session_id, phase, model)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(f"# Raw output: {model} / {phase}\n\n{content}")

    def save_fragments(self, session_id: str, phase: str, fragments: list[Fragment]) -> None:
        """Save extracted fragments for a phase."""
        path = self._fragments_path(session_id, phase)
        data = [f.to_dict() for f in fragments]
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def load_fragments(self, session_id: str, phase: str | None = None) -> list[Fragment]:
        """Load fragments for a session, optionally filtered by phase."""
        sdir = self._session_dir(session_id)
        if not sdir.exists():
            return []

        fragments = []
        pattern = f"fragments-{phase}.yaml" if phase else "fragments-*.yaml"
        for path in sorted(sdir.glob(pattern)):
            with open(path) as f:
                data = yaml.safe_load(f) or []
            fragments.extend(Fragment.from_dict(d) for d in data)
        return fragments

    def list_sessions(self) -> list[Session]:
        """List all sessions."""
        sessions = []
        for meta in sorted(self.dir.glob("*/session.yaml")):
            with open(meta) as f:
                data = yaml.safe_load(f)
            if data:
                sessions.append(Session.from_dict(data))
        return sessions

    def render_log(self, session: Session, fragments: list[Fragment]) -> str:
        """Render a session log as markdown."""
        lines = [
            f"# Edge-Finding Session Log: {session.session_id}",
            "",
            f"**Date:** {session.created}",
            f"**Analyst:** {session.analyst or 'Not specified'}",
            f"**Domain:** {session.domain or 'Not specified'}",
            f"**Models:** {', '.join(session.models_used)}",
            f"**Status:** {session.status}",
            "",
            f"**Entities loaded:** {session.entity_count}",
            f"**Relationships:** {session.relationship_count}",
            f"**Phases completed:** {', '.join(session.phases_completed) or 'None'}",
            "",
            "---",
            "",
        ]

        # Group fragments by phase then model
        by_phase: dict[str, dict[str, list[Fragment]]] = {}
        for f in fragments:
            by_phase.setdefault(f.phase, {}).setdefault(f.source_model, []).append(f)

        for phase, by_model in sorted(by_phase.items()):
            lines.append(f"## Phase: {phase}")
            lines.append("")
            for model, frags in sorted(by_model.items()):
                lines.append(f"### Model: {model}")
                lines.append("")
                for f in frags:
                    status_tag = f" [{f.validation_status}]" if f.validation_status != "unvalidated" else ""
                    lines.append(f"- **{f.id}**{status_tag}: {f.content}")
                lines.append("")

        if session.notes:
            lines.extend(["---", "", "## Analyst Notes", "", session.notes])

        return "\n".join(lines)
