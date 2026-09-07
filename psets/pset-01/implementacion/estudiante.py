from datetime import datetime, timedelta

from regla_prioridad import PrioridadAntes18, SinPrioridad
from reserva import Reserva
from usuario import Usuario


class Estudiante(Usuario):
    MAX_RESERVAS_SEMANA = 2
    MAX_NO_SHOWS_MES = 2

    def __init__(self, nombre, email, contrasena, regla_prioridad=None):
        super().__init__(nombre, email, contrasena)
        self.reservas = []
        self.no_shows = []
        self.bloqueado = False
        self.bloqueado_hasta = None
        self.regla_prioridad = regla_prioridad or SinPrioridad()

    def esta_bloqueado(self, fecha):
        return self.bloqueado or (
            self.bloqueado_hasta is not None and fecha <= self.bloqueado_hasta
        )

    def puede_reservar(self, inicio):
        if self.esta_bloqueado(inicio.date()):
            return False, "El estudiante está bloqueado."
        reservas_semana = [
            reserva
            for reserva in self.reservas
            if reserva.estado == Reserva.ACTIVA
            and reserva.inicio.isocalendar()[:2] == inicio.isocalendar()[:2]
        ]
        if len(reservas_semana) >= self.MAX_RESERVAS_SEMANA:
            return False, "Ya alcanzó el máximo de 2 reservas semanales."
        if inicio.hour < 18 and not self.regla_prioridad.tiene_prioridad(inicio.time()):
            return False, "Antes de las 18:00 solo pueden reservar estudiantes con prioridad."
        return True, "Puede reservar."

    def reservar_cancha(self, cancha, disponibilidad, inicio, fin, momento=None, minutos_proceso=0):
        momento = momento or datetime.combine(inicio.date(), inicio.time())
        permitido, razon = self.puede_reservar(inicio)
        if not permitido:
            return None, razon
        if not cancha.esta_habilitada():
            return None, "La cancha no está habilitada."
        if disponibilidad not in cancha.disponibilidades:
            return None, "El horario no pertenece a la cancha."
        if not disponibilidad.bloquear(momento):
            return None, "El horario no está disponible."
        if minutos_proceso > 15:
            disponibilidad.esta_disponible(momento + timedelta(minutes=minutos_proceso))
            return None, "El proceso excedió 15 minutos; el horario fue liberado."

        reserva = Reserva(self, cancha, disponibilidad, inicio, fin)
        disponibilidad.confirmar_reserva(reserva)
        self.reservas.append(reserva)
        return reserva, "Reserva confirmada."

    def cancelar_reserva(self, reserva, momento):
        if reserva not in self.reservas:
            return False, "Un estudiante solo puede cancelar sus propias reservas."
        if reserva.estado != Reserva.ACTIVA:
            return False, "La reserva ya no está activa."
        if reserva.inicio - momento >= timedelta(hours=2):
            reserva.cancelar()
            return True, "Reserva cancelada normalmente."
        reserva.marcar_no_show()
        self.registrar_no_show(momento)
        return True, "Cancelación tardía: se registró un no-show."

    def registrar_no_show(self, fecha):
        if isinstance(fecha, datetime):
            fecha = fecha.date()
        self.no_shows.append(fecha)
        del_mes = [
            no_show
            for no_show in self.no_shows
            if no_show.year == fecha.year and no_show.month == fecha.month
        ]
        if len(del_mes) >= self.MAX_NO_SHOWS_MES:
            siguiente_mes = (fecha.replace(day=28) + timedelta(days=4)).replace(day=1)
            self.bloqueado_hasta = siguiente_mes - timedelta(days=1)


class Capitan(Estudiante):
    def __init__(self, nombre, email, contrasena, equipo):
        super().__init__(nombre, email, contrasena, PrioridadAntes18())
        self.equipo = equipo
