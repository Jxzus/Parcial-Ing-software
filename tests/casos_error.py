"""Batería de defectos de contenido: (nombre, mutador, código esperado, fragmento de referencia)."""


def _escena(d, eid):
    return next(e for e in d["escenas"] if e["id"] == eid)


def _opcion(d, eid, oid):
    return next(o for o in _escena(d, eid)["opciones"] if o["id"] == oid)


def _nueva_opcion():
    return {"id": "extra", "texto": "Extra", "destino": "E1", "condiciones": {}, "efectos": {}}


CASOS_ERROR = [
    ("inicio_inexistente", lambda d: d.__setitem__("inicio", "E99"),
     "INICIO_INEXISTENTE", "inicio"),
    ("campo_titulo_ausente", lambda d: d.pop("titulo"),
     "CAMPO_AUSENTE", "titulo"),
    ("campo_escenas_ausente", lambda d: d.pop("escenas"),
     "CAMPO_AUSENTE", "escenas"),
    ("campo_texto_de_escena_ausente", lambda d: _escena(d, "E1").pop("texto"),
     "CAMPO_AUSENTE", "E1"),
    ("campo_destino_de_opcion_ausente", lambda d: _opcion(d, "E1", "revisar").pop("destino"),
     "CAMPO_AUSENTE", "revisar"),
    ("escenas_no_es_lista", lambda d: d.__setitem__("escenas", "hola"),
     "ESTRUCTURA_INVALIDA", "escenas"),
    ("escena_duplicada", lambda d: d["escenas"].append(dict(_escena(d, "E6"))),
     "ESCENA_DUPLICADA", "E6"),
    ("opcion_duplicada",
     lambda d: _escena(d, "E2")["opciones"].append(dict(_opcion(d, "E2", "investigar"))),
     "OPCION_DUPLICADA", "investigar"),
    ("destino_inexistente", lambda d: _opcion(d, "E3", "cortar").__setitem__("destino", "E99"),
     "DESTINO_INEXISTENTE", "E99"),
    ("variable_no_declarada_en_condicion",
     lambda d: _opcion(d, "E3", "cortar").__setitem__("condiciones", {"fantasma": True}),
     "VARIABLE_NO_DECLARADA", "fantasma"),
    ("variable_no_declarada_en_efecto",
     lambda d: _opcion(d, "E2", "continuar").__setitem__("efectos", {"fantasma": True}),
     "VARIABLE_NO_DECLARADA", "fantasma"),
    ("valor_no_booleano_en_efecto",
     lambda d: _opcion(d, "E2", "investigar").__setitem__("efectos", {"conoce_origen": "si"}),
     "VALOR_NO_BOOLEANO", "conoce_origen"),
    ("valor_no_booleano_en_condicion",
     lambda d: _opcion(d, "E3", "activar_codigo").__setitem__("condiciones", {"conoce_origen": 1}),
     "VALOR_NO_BOOLEANO", "conoce_origen"),
    ("valor_no_booleano_en_variable_inicial",
     lambda d: d["variables"].__setitem__("conoce_origen", "no"),
     "VALOR_NO_BOOLEANO", "conoce_origen"),
    ("final_con_opciones", lambda d: _escena(d, "E4")["opciones"].append(_nueva_opcion()),
     "FINAL_CON_OPCIONES", "E4"),
    ("no_final_sin_opciones", lambda d: _escena(d, "E1")["opciones"].clear(),
     "NO_FINAL_SIN_OPCIONES", "E1"),
]
