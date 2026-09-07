class Reserva:
    ACTIVA = "ACTIVA"
    CANCELADA = "CANCELADA"
    NO_SHOW = "NO_SHOW"

    def __init__(self, estudiante, cancha, disponibilidad, inicio, fin):
        self.estudiante = estudiante
        self.cancha = cancha
        self.disponibilidad = disponibilidad
        self.inicio = inicio
        self.fin = fin
        self.estado = self.ACTIVA

    def cancelar(self):
        if self.estado != self.ACTIVA:
            return False
        self.estado = self.CANCELADA
        self.disponibilidad.liberar()
        return True

    def marcar_no_show(self):
        if self.estado != self.ACTIVA:
            return False
        self.estado = self.NO_SHOW
        self.disponibilidad.liberar()
        return True
