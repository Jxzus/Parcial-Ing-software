"""Lectura de archivos y construcción de la Historia (solo si es válida)."""
import json
from pathlib import Path

from motor.errores import ErrorContenido, HistoriaInvalida
from motor.modelo import Escena, Historia, Opcion
from motor.validador import validar


def leer_json(ruta):
    ruta = Path(ruta)
    try:
        with ruta.open(encoding="utf-8") as f:
            return json.load(f)
    except OSError as exc:
        causa = f"No se pudo abrir el archivo: {exc.strerror or exc}."
    except UnicodeDecodeError:
        causa = "El archivo no está codificado en UTF-8."
    except json.JSONDecodeError as exc:
        causa = f"JSON mal formado (línea {exc.lineno}, columna {exc.colno}): {exc.msg}."
    raise HistoriaInvalida([ErrorContenido("ARCHIVO_ILEGIBLE", causa, str(ruta))])


def construir_historia(datos):
    """Valida y construye la Historia; lanza HistoriaInvalida si hay errores."""
    errores = validar(datos)
    if errores:
        raise HistoriaInvalida(errores)
    escenas = {}
    for e in datos["escenas"]:
        opciones = tuple(
            Opcion(o["id"], o["texto"], o["destino"],
                   dict(o["condiciones"]), dict(o["efectos"]))
            for o in e["opciones"]
        )
        escenas[e["id"]] = Escena(e["id"], e["texto"], e["final"], opciones)
    return Historia(datos["titulo"], datos["inicio"], dict(datos["variables"]), escenas)


def cargar_historia(ruta):
    return construir_historia(leer_json(ruta))
