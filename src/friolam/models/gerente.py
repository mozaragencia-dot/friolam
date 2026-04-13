"""Modelo del gerente."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Gerente:
    """Representa un gerente de área."""

    nombre: str
    area: str
    objetivos_trimestrales: int

    def resumen(self) -> str:
        return (
            f"{self.nombre} lidera {self.area} con "
            f"{self.objetivos_trimestrales} objetivos trimestrales."
        )
