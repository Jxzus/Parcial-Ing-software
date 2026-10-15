"""Validación del contenido. Función pura: recibe datos, devuelve lista de errores."""
from motor.errores import ErrorContenido

CAMPOS_HISTORIA = ("titulo", "inicio", "variables", "escenas")
CAMPOS_ESCENA = ("id", "texto", "final", "opciones")
CAMPOS_OPCION = ("id", "texto", "destino", "condiciones", "efectos")


def _err(errores, codigo, mensaje, referencia=""):
    errores.append(ErrorContenido(codigo, mensaje, referencia))


def _campos_obligatorios(obj, campos, ambito, errores):
    for campo in campos:
        if campo not in obj:
            _err(errores, "CAMPO_AUSENTE",
                 f"Falta el campo obligatorio '{campo}'.", f"{ambito}.{campo}")


def _variables_declaradas(datos, errores):
    variables = datos.get("variables")
    if "variables" not in datos:
        return set()
    if not isinstance(variables, dict):
        _err(errores, "ESTRUCTURA_INVALIDA",
             "'variables' debe ser un mapa de nombre a booleano.", "variables")
        return set()
    for nombre, valor in variables.items():
        if not isinstance(valor, bool):
            _err(errores, "VALOR_NO_BOOLEANO",
                 f"El valor inicial de '{nombre}' debe ser true o false.",
                 f"variables.{nombre}")
    return set(variables)


def _ids_escenas(escenas, errores):
    vistos, repetidos = set(), set()
    for i, esc in enumerate(escenas):
        if not isinstance(esc, dict):
            _err(errores, "ESTRUCTURA_INVALIDA",
                 "Cada escena debe ser un objeto.", f"escenas[{i}]")
            continue
        eid = esc.get("id")
        if isinstance(eid, str):
            if eid in vistos and eid not in repetidos:
                repetidos.add(eid)
                _err(errores, "ESCENA_DUPLICADA",
                     f"El identificador de escena '{eid}' está repetido.", eid)
            vistos.add(eid)
    return vistos


def _validar_mapa(mapa, nombre, ref, declaradas, errores):
    if not isinstance(mapa, dict):
        _err(errores, "ESTRUCTURA_INVALIDA",
             f"'{nombre}' debe ser un mapa de variable a booleano.", f"{ref}.{nombre}")
        return
    for var, valor in mapa.items():
        if var not in declaradas:
            _err(errores, "VARIABLE_NO_DECLARADA",
                 f"La variable '{var}' no está declarada en 'variables'.",
                 f"{ref}.{nombre}.{var}")
        if not isinstance(valor, bool):
            _err(errores, "VALOR_NO_BOOLEANO",
                 f"El valor de '{var}' en '{nombre}' debe ser true o false.",
                 f"{ref}.{nombre}.{var}")


def _validar_opcion(op, i, ref_escena, ids, declaradas, errores):
    if not isinstance(op, dict):
        _err(errores, "ESTRUCTURA_INVALIDA",
             "Cada opción debe ser un objeto.", f"{ref_escena}.opciones[{i}]")
        return
    oid = op.get("id", f"#{i}")
    ref = f"{ref_escena}.{oid}"
    _campos_obligatorios(op, CAMPOS_OPCION, ref, errores)
    destino = op.get("destino")
    if "destino" in op and not (isinstance(destino, str) and destino in ids):
        _err(errores, "DESTINO_INEXISTENTE",
             f"El destino '{destino}' no corresponde a ninguna escena.", f"{ref}.destino")
    for clave in ("condiciones", "efectos"):
        if clave in op:
            _validar_mapa(op[clave], clave, ref, declaradas, errores)


def _validar_escena(esc, i, ids, declaradas, errores):
    if not isinstance(esc, dict):
        return
    eid = esc.get("id", f"#{i}")
    ref = f"escena {eid}"
    _campos_obligatorios(esc, CAMPOS_ESCENA, ref, errores)
    if "final" in esc and not isinstance(esc["final"], bool):
        _err(errores, "VALOR_NO_BOOLEANO",
             "'final' debe ser true o false.", f"{ref}.final")
    opciones = esc.get("opciones")
    if "opciones" not in esc:
        return
    if not isinstance(opciones, list):
        _err(errores, "ESTRUCTURA_INVALIDA",
             "'opciones' debe ser una lista.", f"{ref}.opciones")
        return
    vistos, repetidos = set(), set()
    for j, op in enumerate(opciones):
        if isinstance(op, dict) and isinstance(op.get("id"), str):
            oid = op["id"]
            if oid in vistos and oid not in repetidos:
                repetidos.add(oid)
                _err(errores, "OPCION_DUPLICADA",
                     f"La opción '{oid}' está repetida en la escena '{eid}'.",
                     f"{ref}.{oid}")
            vistos.add(oid)
        _validar_opcion(op, j, ref, ids, declaradas, errores)
    if esc.get("final") is True and opciones:
        _err(errores, "FINAL_CON_OPCIONES",
             f"La escena final '{eid}' debe tener cero opciones.", ref)
    if esc.get("final") is False and not opciones:
        _err(errores, "NO_FINAL_SIN_OPCIONES",
             f"La escena no final '{eid}' debe tener al menos una opción.", ref)


def validar(datos):
    """Devuelve la lista de ErrorContenido; vacía si la historia es válida."""
    errores = []
    if not isinstance(datos, dict):
        _err(errores, "ESTRUCTURA_INVALIDA",
             "La raíz del archivo debe ser un objeto.", "raíz")
        return errores
    _campos_obligatorios(datos, CAMPOS_HISTORIA, "historia", errores)
    declaradas = _variables_declaradas(datos, errores)
    escenas = datos.get("escenas", [])
    if "escenas" in datos and not isinstance(escenas, list):
        _err(errores, "ESTRUCTURA_INVALIDA",
             "'escenas' debe ser una lista.", "escenas")
        escenas = []
    ids = _ids_escenas(escenas, errores)
    inicio = datos.get("inicio")
    if "inicio" in datos and not (isinstance(inicio, str) and inicio in ids):
        _err(errores, "INICIO_INEXISTENTE",
             f"La escena inicial '{inicio}' no existe.", "inicio")
    for i, esc in enumerate(escenas):
        _validar_escena(esc, i, ids, declaradas, errores)
    return errores
