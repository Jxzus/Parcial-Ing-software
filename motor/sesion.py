"""Sesión de juego: estado actual de una partida sobre una Historia."""
from motor.errores import OpcionNoDisponible


class Sesion:
    def __init__(self, historia):
        self._historia = historia
        self.reiniciar()

    def reiniciar(self):
        self._escena_id = self._historia.inicio
        self._variables = dict(self._historia.variables)

    @property
    def escena_actual(self):
        return self._historia.escenas[self._escena_id]

    @property
    def variables(self):
        return dict(self._variables)

    @property
    def es_final(self):
        return self.escena_actual.final

    def opciones_habilitadas(self):
        return [o for o in self.escena_actual.opciones if o.habilitada(self._variables)]

    @property
    def bloqueada(self):
        """Escena no final sin opciones habilitadas."""
        return not self.es_final and not self.opciones_habilitadas()

    def elegir(self, opcion_id):
        """Aplica efectos y avanza. Si la opción no está disponible, no cambia nada."""
        habilitadas = {o.id: o for o in self.opciones_habilitadas()}
        if opcion_id not in habilitadas:
            raise OpcionNoDisponible(
                f"La opción '{opcion_id}' no existe o no está habilitada en la escena "
                f"'{self._escena_id}'.")
        opcion = habilitadas[opcion_id]
        self._variables = {**self._variables, **opcion.efectos}
        self._escena_id = opcion.destino
