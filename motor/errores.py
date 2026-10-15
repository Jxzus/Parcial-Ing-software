"""Errores del motor. Cada error de contenido lleva código, mensaje y referencia."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorContenido:
    codigo: str
    mensaje: str
    referencia: str = ""

    def __str__(self) -> str:
        ref = f" [{self.referencia}]" if self.referencia else ""
        return f"{self.codigo}{ref}: {self.mensaje}"


class HistoriaInvalida(Exception):
    """El archivo de historia no es válido; contiene todos los errores hallados."""

    def __init__(self, errores):
        self.errores = list(errores)
        super().__init__("\n".join(str(e) for e in self.errores))


class OpcionNoDisponible(Exception):
    """La opción no existe o no está habilitada en el estado actual."""
