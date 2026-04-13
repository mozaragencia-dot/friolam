"""Backend de alto volumen para Friolam usando un archivo SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class FriolamBackend:
    """Backend file-based con soporte para gran volumen de registros."""

    def __init__(self, db_file: str) -> None:
        self.db_file = db_file
        Path(db_file).parent.mkdir(parents=True, exist_ok=True)
        self._setup()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA temp_store=MEMORY")
        return conn

    def _setup(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    nombre TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value INTEGER NOT NULL,
                    UNIQUE(role, nombre)
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_records_role ON records(role)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_records_nombre ON records(nombre)")

        if self.count_records() == 0:
            self.seed_defaults()

    def seed_defaults(self) -> None:
        self.upsert_record("tecnico", "Ana", "tickets_abiertos", 5)
        self.upsert_record("administrador", "Luis", "sistemas_activos", 12)
        self.upsert_record("gerente", "María", "objetivos_trimestrales", 4)

    def upsert_record(
        self,
        role: str,
        nombre: str,
        metric_name: str,
        metric_value: int,
    ) -> int:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO records(role, nombre, metric_name, metric_value)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(role, nombre)
                DO UPDATE SET metric_name = excluded.metric_name,
                              metric_value = excluded.metric_value
                """,
                (role, nombre, metric_name, metric_value),
            )
            row = conn.execute(
                "SELECT id FROM records WHERE role = ? AND nombre = ?", (role, nombre)
            ).fetchone()
            return int(row["id"])

    def get_record(self, record_id: int) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, role, nombre, metric_name, metric_value FROM records WHERE id = ?",
                (record_id,),
            ).fetchone()
        if row is None:
            return None
        return dict(row)

    def list_records(
        self,
        role: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 500))
        offset = max(0, offset)
        with self._connect() as conn:
            if role:
                rows = conn.execute(
                    """
                    SELECT id, role, nombre, metric_name, metric_value
                    FROM records
                    WHERE role = ?
                    ORDER BY id
                    LIMIT ? OFFSET ?
                    """,
                    (role, limit, offset),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT id, role, nombre, metric_name, metric_value
                    FROM records
                    ORDER BY id
                    LIMIT ? OFFSET ?
                    """,
                    (limit, offset),
                ).fetchall()
        return [dict(r) for r in rows]


    def summary_by_role(self) -> dict[str, int]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT role, COUNT(*) AS total FROM records GROUP BY role ORDER BY role"
            ).fetchall()
        return {str(r["role"]): int(r["total"]) for r in rows}

    def count_records(self, role: str | None = None) -> int:
        with self._connect() as conn:
            if role:
                row = conn.execute(
                    "SELECT COUNT(*) AS total FROM records WHERE role = ?", (role,)
                ).fetchone()
            else:
                row = conn.execute("SELECT COUNT(*) AS total FROM records").fetchone()
        return int(row["total"])


def default_backend() -> FriolamBackend:
    return FriolamBackend("data/friolam_gigante.db")
