"""Punto de entrada: python main.py [ruta_historia] [--validar]"""
import argparse
import sys

from motor import HistoriaInvalida, cargar_historia
from motor.cli import jugar


def main(argv=None):
    p = argparse.ArgumentParser(description="Motor de historias interactivas")
    p.add_argument("ruta", nargs="?", default="historias/la_ultima_transmision.json")
    p.add_argument("--validar", action="store_true", help="solo valida el archivo")
    args = p.parse_args(argv)
    try:
        historia = cargar_historia(args.ruta)
    except HistoriaInvalida as exc:
        print(f"El archivo '{args.ruta}' no es válido ({len(exc.errores)} error(es)):",
              file=sys.stderr)
        for e in exc.errores:
            print(f"  - {e}", file=sys.stderr)
        return 1
    if args.validar:
        print(f"'{args.ruta}' es válido: {len(historia.escenas)} escenas.")
        return 0
    jugar(historia)
    return 0


if __name__ == "__main__":
    sys.exit(main())
