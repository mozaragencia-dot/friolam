"""Backend de persistencia para Friolam (SQLite)."""

from __future__ import annotations

import sqlite3
from pathlib import Path


class FriolamBackend:
    """Simple backend layer backed by SQLite."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._ensure_schema()
        self._ensure_seed_data()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS roles (
                    role TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    detalle_1 TEXT NOT NULL,
                    detalle_2 INTEGER NOT NULL
                )
                """
            )

    def _ensure_seed_data(self) -> None:
        defaults = {
            "tecnico": ("Ana", "Redes", 5),
            "administrador": ("Luis", "Sistemas activos", 12),
            "gerente": ("María", "Objetivos trimestrales", 4),
        }
        with self._connect() as conn:
            for role, values in defaults.items():
                conn.execute(
                    """
                    INSERT INTO roles(role, nombre, detalle_1, detalle_2)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(role) DO NOTHING
                    """,
                    (role, values[0], values[1], values[2]),
                )

    def get_role(self, role: str) -> dict[str, str | int]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT role, nombre, detalle_1, detalle_2 FROM roles WHERE role = ?",
                (role,),
            ).fetchone()
        if row is None:
            raise KeyError(role)
        return {
            "role": row["role"],
            "nombre": row["nombre"],
            "detalle_1": row["detalle_1"],
            "detalle_2": row["detalle_2"],
        }

    def get_all_roles(self) -> list[dict[str, str | int]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT role, nombre, detalle_1, detalle_2 FROM roles ORDER BY role"
            ).fetchall()
        return [
            {
                "role": row["role"],
                "nombre": row["nombre"],
                "detalle_1": row["detalle_1"],
                "detalle_2": row["detalle_2"],
            }
            for row in rows
        ]


def default_backend() -> FriolamBackend:
    """Create backend in local data directory."""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    return FriolamBackend(str(data_dir / "friolam.db"))
