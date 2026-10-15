"""Pruebas unitarias U1 a U5 (y criterios de aceptación CA02 y CA03)."""
import copy
import pytest

from motor import (HistoriaInvalida, OpcionNoDisponible, Sesion, cargar_historia,
                   construir_historia)
from motor.validador import validar
from tests.casos_error import CASOS_ERROR
from tests.conftest import jugar_ruta


# --- U1: las condiciones habilitan únicamente las opciones correspondientes -----------
@pytest.mark.parametrize("ruta, esperadas", [
    (["revisar", "investigar"], ["activar_codigo", "cortar"]),            # conoce_origen = True (CA01)
    (["revisar", "continuar"], ["activar_sin_verificar", "cortar"]),      # conoce_origen = False
])
def test_u1_condiciones_habilitan_solo_opciones_correspondientes(sesion, ruta, esperadas):
    jugar_ruta(sesion, *ruta)
    assert sesion.escena_actual.id == "E3"
    assert [o.id for o in sesion.opciones_habilitadas()] == esperadas
    assert len(sesion.opciones_habilitadas()) == 2


# --- U2: una elección válida aplica efectos y avanza al destino ----------------------
def test_u2_eleccion_valida_aplica_efectos_y_avanza(sesion):
    sesion.elegir("revisar")
    assert sesion.escena_actual.id == "E2"
    assert sesion.variables == {"conoce_origen": False, "confia_en_la_voz": False}
    sesion.elegir("investigar")
    assert sesion.escena_actual.id == "E3"
    assert sesion.variables["conoce_origen"] is True
    sesion.elegir("activar_codigo")
    assert sesion.escena_actual.id == "E4"
    assert sesion.variables == {"conoce_origen": True, "confia_en_la_voz": True}
    assert sesion.es_final


def test_u2_el_estado_persiste_entre_escenas(sesion):
    """N04: lo ocurrido en E2 sigue vigente en E3 y condiciona sus opciones."""
    sesion.elegir("revisar")
    sesion.elegir("investigar")                    # efecto: conoce_origen = True
    assert sesion.escena_actual.id == "E3"
    assert sesion.variables["conoce_origen"] is True
    assert "activar_codigo" in [o.id for o in sesion.opciones_habilitadas()]
    assert "activar_sin_verificar" not in [o.id for o in sesion.opciones_habilitadas()]


# --- U3: opción inexistente o no habilitada deja intacto el estado (incluye CA02) ----
@pytest.mark.parametrize("ruta, opcion_invalida", [
    ([], "no_existe"),
    ([], ""),
    ([], "investigar"),                                  # existe, pero en otra escena
    (["revisar", "continuar"], "activar_codigo"),        # CA02: no habilitada sin conocer origen
    (["revisar", "investigar"], "activar_sin_verificar"),  # no habilitada conociendo origen
])
def test_u3_opcion_invalida_no_altera_estado(sesion, ruta, opcion_invalida):
    jugar_ruta(sesion, *ruta)
    antes = (sesion.escena_actual.id, sesion.variables)
    with pytest.raises(OpcionNoDisponible):
        sesion.elegir(opcion_invalida)
    assert (sesion.escena_actual.id, sesion.variables) == antes


def test_u3_activar_sin_verificar_lleva_a_e5(sesion):
    jugar_ruta(sesion, "revisar", "continuar", "activar_sin_verificar")
    assert sesion.escena_actual.id == "E5" and sesion.es_final


# --- U4: errores de contenido producen rechazo controlado ----------------------------
@pytest.mark.parametrize("nombre, mutador, codigo, fragmento", CASOS_ERROR,
                         ids=[c[0] for c in CASOS_ERROR])
def test_u4_errores_de_contenido_se_rechazan(datos, nombre, mutador, codigo, fragmento):
    mutador(datos)
    with pytest.raises(HistoriaInvalida) as exc:
        construir_historia(datos)
    errores = exc.value.errores
    assert codigo in {e.codigo for e in errores}
    # el mensaje o la referencia identifican el campo o ID involucrado
    assert any(e.codigo == codigo and fragmento in f"{e.referencia} {e.mensaje}"
               for e in errores)


def test_u4_archivo_inexistente(tmp_path):
    with pytest.raises(HistoriaInvalida) as exc:
        cargar_historia(tmp_path / "no_existe.json")
    assert exc.value.errores[0].codigo == "ARCHIVO_ILEGIBLE"


@pytest.mark.parametrize("contenido", ['{"titulo": "x", ', "esto no es json", ""])
def test_u4_archivo_ilegible(tmp_path, contenido):
    ruta = tmp_path / "roto.json"
    ruta.write_text(contenido, encoding="utf-8")
    with pytest.raises(HistoriaInvalida) as exc:
        cargar_historia(ruta)
    assert exc.value.errores[0].codigo == "ARCHIVO_ILEGIBLE"


@pytest.mark.parametrize("contenido", ["[]", '"texto"', "42", "null"])
def test_u4_estructura_incorrecta_en_raiz(tmp_path, contenido):
    ruta = tmp_path / "raiz.json"
    ruta.write_text(contenido, encoding="utf-8")
    with pytest.raises(HistoriaInvalida) as exc:
        cargar_historia(ruta)
    assert exc.value.errores[0].codigo == "ESTRUCTURA_INVALIDA"


def test_u4_ca03_destino_e99_no_abre_sesion(datos):
    datos["escenas"][1]["opciones"][0]["destino"] = "E99"
    sesion = None
    with pytest.raises(HistoriaInvalida) as exc:
        sesion = Sesion(construir_historia(datos))
    assert sesion is None
    assert "E99" in str(exc.value)


def test_u4_historia_valida_no_tiene_errores(datos):
    assert validar(datos) == []


# --- U5: reiniciar restaura escena y variables iniciales -----------------------------
def test_u5_reiniciar_restaura_estado_inicial(sesion):
    jugar_ruta(sesion, "revisar", "investigar", "activar_codigo")
    assert sesion.es_final
    sesion.reiniciar()
    assert sesion.escena_actual.id == "E1"
    assert sesion.variables == {"conoce_origen": False, "confia_en_la_voz": False}
    assert [o.id for o in sesion.opciones_habilitadas()] == ["revisar"]


# --- Escena no final sin opciones habilitadas durante la partida ---------------------
def test_escena_bloqueada_se_informa_y_permite_reiniciar(datos):
    # Defecto de diseño que el validador no analiza: la única opción exige un valor imposible.
    datos["escenas"][0]["opciones"][0]["condiciones"] = {"conoce_origen": True}
    sesion = Sesion(construir_historia(datos))
    assert sesion.bloqueada and not sesion.es_final
    assert sesion.opciones_habilitadas() == []
    with pytest.raises(OpcionNoDisponible):
        sesion.elegir("revisar")
    sesion.reiniciar()
    assert sesion.escena_actual.id == "E1"


def test_finales_no_tienen_opciones(historia):
    for eid in ("E4", "E5", "E6"):
        assert historia.escenas[eid].final and historia.escenas[eid].opciones == ()