import copy
import json
from pathlib import Path

import pytest

from motor import Sesion, cargar_historia

RAIZ = Path(__file__).resolve().parent.parent
RUTA_HISTORIA = RAIZ / "historias" / "la_ultima_transmision.json"
RUTA_SEGUNDA = RAIZ / "historias" / "segunda_transmision.json"


@pytest.fixture
def datos():
    """Copia fresca del contenido de la historia de referencia (como dict)."""
    with RUTA_HISTORIA.open(encoding="utf-8") as f:
        return copy.deepcopy(json.load(f))


@pytest.fixture
def historia():
    return cargar_historia(RUTA_HISTORIA)


@pytest.fixture
def sesion(historia):
    return Sesion(historia)


def jugar_ruta(sesion, *ids):
    for i in ids:
        sesion.elegir(i)
    return sesion
