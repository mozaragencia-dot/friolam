"""Modelo del técnico."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Tecnico:
    """Representa un técnico operativo."""

    nombre: str
    especialidad: str
    tickets_abiertos: int

    def resumen(self) -> str:
        return (
            f"{self.nombre} ({self.especialidad}) tiene "
            f"{self.tickets_abiertos} tickets abiertos."
        )
