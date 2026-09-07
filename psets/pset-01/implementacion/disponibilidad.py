from datetime import timedelta


class Disponibilidad:
    LIMITE_PROCESO = timedelta(minutes=15)

    def __init__(self, fecha, hora_inicio, hora_fin, disponible=True):
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.disponible = disponible
        self.reserva = None
        self.bloqueada_en = None

    def esta_disponible(self, momento=None):
        if self.reserva is not None:
            return False
        if self.bloqueada_en is not None:
            if momento is not None and momento - self.bloqueada_en > self.LIMITE_PROCESO:
                self.liberar()
            else:
                return False
        return self.disponible

    def bloquear(self, momento):
        if not self.esta_disponible(momento):
            return False
        self.disponible = False
        self.bloqueada_en = momento
        return True

    def confirmar_reserva(self, reserva):
        self.reserva = reserva
        self.bloqueada_en = None

    def liberar(self):
        self.disponible = True
        self.reserva = None
        self.bloqueada_en = None
