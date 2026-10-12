from datetime import timedelta
from threading import Lock


class ConfiguracionTecnologia:
    _instancia = None
    _lock = Lock()

    def __new__(cls):
        if cls._instancia is None:
            with cls._lock:
                if cls._instancia is None:
                    instancia = super().__new__(cls)
                    instancia.hora_prioridad = 18
                    instancia.horas_cancelacion_estudiante = 2
                    instancia.horas_cancelacion_capitan = 24
                    instancia.no_shows_para_suspension = 3
                    instancia.dias_suspension = 7
                    cls._instancia = instancia
        return cls._instancia

    @classmethod
    def obtener_instancia(cls):
        return cls()


class EstrategiaPrioridad:
    def tiene_prioridad(self, momento):
        raise NotImplementedError


class PrioridadAntes18(EstrategiaPrioridad):
    def tiene_prioridad(self, momento):
        config = ConfiguracionTecnologia.obtener_instancia()
        return momento.hour < config.hora_prioridad


class SinPrioridad(EstrategiaPrioridad):
    def tiene_prioridad(self, momento):
        return False


class EstrategiaCancelacion:
    def cancelar(self, reserva, momento):
        raise NotImplementedError


class CancelacionEstudiante(EstrategiaCancelacion):
    def cancelar(self, reserva, momento):
        config = ConfiguracionTecnologia.obtener_instancia()
        limite = timedelta(hours=config.horas_cancelacion_estudiante)
        return cancelar_con_limite(reserva, momento, limite)


class CancelacionCapitan(EstrategiaCancelacion):
    def cancelar(self, reserva, momento):
        config = ConfiguracionTecnologia.obtener_instancia()
        limite = timedelta(hours=config.horas_cancelacion_capitan)
        return cancelar_con_limite(reserva, momento, limite)


class CancelacionAdministrativa(EstrategiaCancelacion):
    def cancelar(self, reserva, momento, motivo=""):
        if not reserva.anular_por_administrador(momento, motivo):
            return False, "La reserva ya no está activa."
        return True, "Reserva anulada por administración sin penalidad."


def cancelar_con_limite(reserva, momento, limite):
    if reserva.inicio - momento >= limite:
        reserva.cancelar_sin_penalidad(momento)
        return True, "Reserva cancelada normalmente."
    reserva.marcar_no_show(momento)
    return True, "Cancelación tardía: se registró un no-show."
