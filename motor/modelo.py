"""Modelo de dominio: Historia, Escena y Opcion (inmutables)."""
from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass(frozen=True)
class Opcion:
    id: str
    texto: str
    destino: str
    condiciones: Dict[str, bool] = field(default_factory=dict)
    efectos: Dict[str, bool] = field(default_factory=dict)

    def habilitada(self, variables: Dict[str, bool]) -> bool:
        """Un mapa vacío habilita la opción; todas las igualdades deben cumplirse."""
        return all(variables[k] == v for k, v in self.condiciones.items())


@dataclass(frozen=True)
class Escena:
    id: str
    texto: str
    final: bool
    opciones: Tuple[Opcion, ...] = ()


@dataclass(frozen=True)
class Historia:
    titulo: str
    inicio: str
    variables: Dict[str, bool]
    escenas: Dict[str, Escena]
