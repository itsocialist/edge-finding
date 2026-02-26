"""SQLite storage layer for websets, results, and runs."""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime
from typing import Optional

from schemas import Person, Company

DEFAULT_DB = os.environ.get("WEBSETS_DB", "websets.db")


def _connect(db_path: str = DEFAULT_DB) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(db_path: str = DEFAULT_DB) -> None:
    """Create tables if they don't exist."""
    conn = _connect(db_path)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS websets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT UNIQUE NOT NULL,
            criteria    TEXT NOT NULL,
            entity_type TEXT NOT NULL CHECK(entity_type IN ('person', 'company')),
            created_at  TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS runs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            webset_id   INTEGER NOT NULL REFERENCES websets(id) ON DELETE CASCADE,
            started_at  TEXT NOT NULL,
            finished_at TEXT,
            status      TEXT NOT NULL DEFAULT 'running',
            result_count INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS results (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            webset_id     INTEGER NOT NULL REFERENCES websets(id) ON DELETE CASCADE,
            run_id        INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
            entity_type   TEXT NOT NULL,
            natural_key   TEXT,
            data          TEXT NOT NULL,
            date_captured TEXT NOT NULL
        );

        CREATE UNIQUE INDEX IF NOT EXISTS idx_results_natural_key
            ON results(webset_id, natural_key)
            WHERE natural_key IS NOT NULL;
        """
    )
    conn.commit()
    conn.close()


# ── Webset CRUD ──────────────────────────────────────────────────────────────


def create_webset(name: str, criteria: str, entity_type: str, db_path: str = DEFAULT_DB) -> dict:
    conn = _connect(db_path)
    now = datetime.utcnow().isoformat()
    try:
        conn.execute(
            "INSERT INTO websets (name, criteria, entity_type, created_at) VALUES (?, ?, ?, ?)",
            (name, criteria, entity_type, now),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError(f"Webset '{name}' already exists")
    row = conn.execute("SELECT * FROM websets WHERE name = ?", (name,)).fetchone()
    conn.close()
    return dict(row)


def get_webset(name: str, db_path: str = DEFAULT_DB) -> Optional[dict]:
    conn = _connect(db_path)
    row = conn.execute("SELECT * FROM websets WHERE name = ?", (name,)).fetchone()
    conn.close()
    return dict(row) if row else None


def list_websets(db_path: str = DEFAULT_DB) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute("SELECT * FROM websets ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_webset(name: str, db_path: str = DEFAULT_DB) -> bool:
    conn = _connect(db_path)
    cur = conn.execute("DELETE FROM websets WHERE name = ?", (name,))
    conn.commit()
    conn.close()
    return cur.rowcount > 0


# ── Runs ─────────────────────────────────────────────────────────────────────


def create_run(webset_id: int, db_path: str = DEFAULT_DB) -> int:
    conn = _connect(db_path)
    now = datetime.utcnow().isoformat()
    cur = conn.execute(
        "INSERT INTO runs (webset_id, started_at, status) VALUES (?, ?, 'running')",
        (webset_id, now),
    )
    conn.commit()
    run_id = cur.lastrowid
    conn.close()
    return run_id


def finish_run(run_id: int, result_count: int, status: str = "completed", db_path: str = DEFAULT_DB) -> None:
    conn = _connect(db_path)
    now = datetime.utcnow().isoformat()
    conn.execute(
        "UPDATE runs SET finished_at = ?, status = ?, result_count = ? WHERE id = ?",
        (now, status, result_count, run_id),
    )
    conn.commit()
    conn.close()


# ── Results ──────────────────────────────────────────────────────────────────


def store_results(
    webset_id: int,
    run_id: int,
    entities: list[Person | Company],
    db_path: str = DEFAULT_DB,
) -> int:
    """Store entities, skipping duplicates by natural key. Returns count of new records."""
    conn = _connect(db_path)
    inserted = 0
    for entity in entities:
        natural_key = entity.natural_key()
        entity_type = "person" if isinstance(entity, Person) else "company"
        data_json = entity.to_json_str()
        now = datetime.utcnow().isoformat()
        try:
            conn.execute(
                """INSERT INTO results (webset_id, run_id, entity_type, natural_key, data, date_captured)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (webset_id, run_id, entity_type, natural_key, data_json, now),
            )
            inserted += 1
        except sqlite3.IntegrityError:
            # Duplicate natural key — update existing record
            if natural_key:
                conn.execute(
                    """UPDATE results SET data = ?, date_captured = ?, run_id = ?
                       WHERE webset_id = ? AND natural_key = ?""",
                    (data_json, now, run_id, webset_id, natural_key),
                )
    conn.commit()
    conn.close()
    return inserted


def get_results(name: str, db_path: str = DEFAULT_DB) -> list[dict]:
    """Return all results for a webset by name."""
    conn = _connect(db_path)
    rows = conn.execute(
        """SELECT r.* FROM results r
           JOIN websets w ON w.id = r.webset_id
           WHERE w.name = ?
           ORDER BY r.date_captured DESC""",
        (name,),
    ).fetchall()
    conn.close()
    out = []
    for row in rows:
        d = dict(row)
        d["data"] = json.loads(d["data"])
        out.append(d)
    return out


def get_results_as_entities(name: str, db_path: str = DEFAULT_DB) -> list[Person | Company]:
    """Return results deserialized back into dataclass instances."""
    rows = get_results(name, db_path)
    entities = []
    for row in rows:
        data = row["data"]
        if row["entity_type"] == "person":
            entities.append(Person.from_dict(data))
        else:
            entities.append(Company.from_dict(data))
    return entities
