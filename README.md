# La última transmisión — Motor de historias interactivas (versión 1)

**Integrantes:** Jesus Andres Perez Fuentes y Juan Francisco De Avila Alfaro
**Curso:** Ingeniería de Software — Parcial práctico

## Requisitos
- Python 3.10 o superior (desarrollado con 3.12).
- Para ejecutar el juego no se necesita ninguna biblioteca externa.
- Para las pruebas: `pytest` (licencia MIT).

## Instalación
```bash
pip install -r requirements.txt
```

## Ejecución
```bash
python main.py                                        # historia de referencia
python main.py historias/segunda_transmision.json     # segunda historia, mismo motor
python main.py historias/la_ultima_transmision.json --validar   # solo valida el archivo
```
En el juego: número de opción, `r` reinicia, `s` sale.

## Pruebas
```bash
python -m pytest -v
```
Resultado de la última ejecución: ver `resultados_pruebas.txt`.

## Formato de contenido (JSON)
```json
{
  "titulo": "texto",
  "inicio": "ID de la escena inicial",
  "variables": {"nombre": false},
  "escenas": [
    {"id": "E1", "texto": "…", "final": false,
     "opciones": [
       {"id": "revisar", "texto": "Revisar señal", "destino": "E2",
        "condiciones": {"nombre": true}, "efectos": {"nombre": true}}
     ]}
  ]
}
```
- `condiciones`: igualdades sobre variables booleanas; todas deben cumplirse. `{}` habilita la opción.
- `efectos`: asignaciones booleanas aplicadas al elegir. `{}` conserva las variables.
- Una escena final tiene `"opciones": []`; una no final tiene al menos una.
- Para escribir una historia nueva basta con crear un `.json` en `historias/` y ejecutarlo con `python main.py ruta`.

## Errores de contenido que se rechazan antes de jugar
Archivo ilegible o mal formado, estructura incorrecta, campo obligatorio ausente, inicio inexistente, escenas u opciones duplicadas, destino inexistente, variable no declarada, valor no booleano, y cantidad de opciones incompatible con el carácter final de la escena. Cada mensaje indica **código**, **causa** y **ubicación** (por ejemplo `DESTINO_INEXISTENTE [escena E2.investigar.destino]`).

## Rutas para demostrar cada final (historia de referencia)
| Final | Elecciones (ids de opción) |
|---|---|
| E4 Rescate | `revisar` → `investigar` → `activar_codigo` |
| E5 El eco | `revisar` → `continuar` → `activar_sin_verificar` |
| E6 Silencio | `revisar` → `continuar` (o `investigar`) → `cortar` |

## Estructura
- `motor/modelo.py` entidades · `motor/validador.py` reglas de validación · `motor/cargador.py` lectura · `motor/sesion.py` estado de la partida · `motor/cli.py` interfaz de consola.
- `historias/` contenido · `tests/` pruebas automatizadas · `main.py` punto de entrada.

## Limitaciones conocidas
- No hay retroceso (acuerdo provisional pendiente de respuesta del cliente).
- No se analiza automáticamente si todos los caminos llegan a un final; solo se detecta el bloqueo durante la partida.
- Sin guardado entre ejecuciones.
