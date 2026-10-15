"""Interfaz de consola. No contiene reglas de la historia."""
from motor.sesion import Sesion


def jugar(historia, entrada=input, salida=print):
    sesion = Sesion(historia)
    salida(f"=== {historia.titulo} ===")
    while True:
        salida(f"\n{sesion.escena_actual.texto}")
        if sesion.es_final or sesion.bloqueada:
            salida("\n-- FIN --" if sesion.es_final else
                   "\n-- Historia bloqueada: no hay opciones disponibles. --")
            try:
                resp = entrada("¿Jugar de nuevo? (r = reiniciar, s = salir) > ").strip().lower()
            except EOFError:
                return
            if resp == "r":
                sesion.reiniciar()
                salida("")
                continue
            if resp == "s":
                return
            salida("Entrada no válida.")
            continue
        opciones = sesion.opciones_habilitadas()
        for n, o in enumerate(opciones, 1):
            salida(f"  {n}. {o.texto}")
        try:
            resp = entrada("Elige (número, r = reiniciar, s = salir) > ").strip().lower()
        except EOFError:
            return
        if resp == "s":
            return
        if resp == "r":
            sesion.reiniciar()
        elif resp.isdecimal() and 1 <= int(resp) <= len(opciones):
            sesion.elegir(opciones[int(resp) - 1].id)
        else:
            salida("Entrada no válida. Escribe el número de una opción.")
