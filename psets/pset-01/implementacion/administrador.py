from disponibilidad import Disponibilidad
from regla_prioridad import PrioridadAntes18
from reserva import Reserva
from usuario import Usuario


class Administrador(Usuario):
    def gestionar_horarios(self, cancha, fecha, hora_inicio, hora_fin):
        disponibilidad = Disponibilidad(fecha, hora_inicio, hora_fin)
        cancha.agregar_disponibilidad(disponibilidad)
        return disponibilidad

    def mover_reserva(self, reserva, nueva_disponibilidad, nuevo_inicio, nuevo_fin, momento):
        if reserva.estado != Reserva.ACTIVA:
            return False, "Solo se pueden mover reservas activas."
        if not reserva.cancha.esta_habilitada() or not nueva_disponibilidad.bloquear(momento):
            return False, "El nuevo horario no está disponible."
        reserva.disponibilidad.liberar()
        reserva.disponibilidad = nueva_disponibilidad
        reserva.inicio = nuevo_inicio
        reserva.fin = nuevo_fin
        nueva_disponibilidad.confirmar_reserva(reserva)
        return True, "Reserva movida."

    def cancelar_reserva(self, reserva):
        if reserva.estado != Reserva.ACTIVA:
            return False, "La reserva ya no está activa."
        reserva.cancelar()
        return True, "Reserva cancelada por administración."

    def bloquear_estudiante(self, estudiante):
        estudiante.bloqueado = True

    def asignar_prioridad(self, estudiante):
        estudiante.regla_prioridad = PrioridadAntes18()
