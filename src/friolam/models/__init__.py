"""Domain models for Friolam roles."""

from .administrador import Administrador
from .gerente import Gerente
from .tecnico import Tecnico

__all__ = ["Tecnico", "Administrador", "Gerente"]
