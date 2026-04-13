"""Modelo del administrador."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Administrador:
    """Representa un administrador de plataforma."""

    nombre: str
    sistemas_activos: int
    incidentes_criticos: int

    def resumen(self) -> str:
        return (
            f"{self.nombre} administra {self.sistemas_activos} sistemas "
            f"con {self.incidentes_criticos} incidentes críticos."
        )
