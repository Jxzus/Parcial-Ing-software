"""Integración I1: archivo real + motor + consola."""
import pytest

from motor import Sesion, cargar_historia
from motor.cli import jugar
from tests.conftest import RUTA_HISTORIA, RUTA_SEGUNDA, jugar_ruta

FINALES = [
    ("E4", ["revisar", "investigar", "activar_codigo"]),
    ("E5", ["revisar", "continuar", "activar_sin_verificar"]),
    ("E6", ["revisar", "continuar", "cortar"]),
    ("E6", ["revisar", "investigar", "cortar"]),
]


@pytest.mark.parametrize("final, ruta", FINALES)
def test_i1_carga_de_archivo_real_y_decisiones_hasta_un_final(final, ruta):
    historia = cargar_historia(RUTA_HISTORIA)          # lectura real del archivo
    sesion = Sesion(historia)
    jugar_ruta(sesion, *ruta)
    assert sesion.es_final and sesion.escena_actual.id == final
    assert sesion.opciones_habilitadas() == []


def test_i1_segunda_historia_funciona_con_el_mismo_motor():
    sesion = Sesion(cargar_historia(RUTA_SEGUNDA))
    jugar_ruta(sesion, "escuchar", "abrir_con_clave")
    assert sesion.escena_actual.id == "A3" and sesion.es_final
    sesion.reiniciar()
    assert [o.id for o in sesion.opciones_habilitadas()] == ["escuchar", "ignorar"]
    jugar_ruta(sesion, "ignorar")
    assert [o.id for o in sesion.opciones_habilitadas()] == ["forzar_compuerta"]
    sesion.elegir("forzar_compuerta")
    assert sesion.escena_actual.id == "A4" and sesion.es_final


def test_i1_consola_recorre_un_final_y_rechaza_entradas_invalidas():
    entradas = iter(["abc", "9", "1", "1", "1", "s"])   # 2 inválidas, luego revisar, investigar, activar con código (E4)
    salida = []
    jugar(cargar_historia(RUTA_HISTORIA), entrada=lambda _: next(entradas), salida=salida.append)
    texto = "\n".join(salida)
    assert texto.count("Entrada no válida") == 2
    assert "reconoce el código de emergencia" in texto and "-- FIN --" in texto
