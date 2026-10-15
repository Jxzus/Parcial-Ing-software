"""Verificación automatizada de los tres RNF (ver informe, sección de requisitos)."""
import itertools
import random
from pathlib import Path

import pytest

from motor import HistoriaInvalida, Sesion, cargar_historia, construir_historia
from motor.cli import jugar
from tests.casos_error import CASOS_ERROR
from tests.conftest import RAIZ, RUTA_HISTORIA


# RNF-01 Modificabilidad: añadir una historia no requiere cambiar código del motor.
def test_rnf01_el_motor_no_contiene_identificadores_de_ninguna_historia():
    prohibidos = ["E1", "E2", "E3", "E4", "E5", "E6", "conoce_origen", "confia_en_la_voz",
                  "A1", "tiene_grabacion", "Aurora"]
    for archivo in (RAIZ / "motor").glob("*.py"):
        codigo = archivo.read_text(encoding="utf-8")
        for token in prohibidos:
            assert token not in codigo, f"{archivo.name} menciona '{token}'"


def test_rnf01_toda_historia_de_la_carpeta_carga_y_llega_a_un_final():
    historias = sorted((RAIZ / "historias").glob("*.json"))
    assert len(historias) >= 2
    for ruta in historias:
        sesion = Sesion(cargar_historia(ruta))
        for _ in range(50):
            if sesion.es_final:
                break
            sesion.elegir(sesion.opciones_habilitadas()[0].id)
        assert sesion.es_final, f"{ruta.name} no alcanzó un final"


# RNF-02 Claridad de errores: 100 % de los defectos catalogados dan código, causa y ubicación.
@pytest.mark.parametrize("nombre, mutador, codigo, fragmento", CASOS_ERROR,
                         ids=[c[0] for c in CASOS_ERROR])
def test_rnf02_cada_error_indica_codigo_causa_y_ubicacion(datos, nombre, mutador, codigo, fragmento):
    mutador(datos)
    with pytest.raises(HistoriaInvalida) as exc:
        construir_historia(datos)
    for e in exc.value.errores:
        assert e.codigo and len(e.mensaje) > 10 and e.referencia


# RNF-03 Confiabilidad: 0 excepciones no controladas ante entradas arbitrarias del lector.
def test_rnf03_consola_resiste_1000_entradas_aleatorias():
    azar = random.Random(2026)
    pool = ["", " ", "0", "1", "2", "3", "99", "-1", "1.5", "abc", "é", "²", "r", "R",
            "\t", "' OR 1=1", "x" * 500]
    contador = itertools.count()

    def entrada(_):
        if next(contador) >= 1000:
            return "s"
        return azar.choice(pool)

    for ruta in sorted((RAIZ / "historias").glob("*.json")):
        contador = itertools.count()
        jugar(cargar_historia(ruta), entrada=entrada, salida=lambda _: None)
