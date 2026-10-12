from contextlib import ExitStack
from datetime import date, datetime, timedelta
import hashlib
import hmac
import secrets
from threading import Lock, RLock

from reglas import (
    ConfiguracionTecnologia,
    PrioridadAntes18,
    SinPrioridad,
)


class Usuario:
    def __init__(self, nombre, email, contrasena):
        self.nombre = nombre
        self.email = email
        self._sal = secrets.token_bytes(16)
        self._contrasena_hash = hashlib.pbkdf2_hmac(
            "sha256", contrasena.encode("utf-8"), self._sal, 100_000
        )
        self.registrado = False
        self.autenticado = False

    def registrarse(self):
        self.registrado = True
        return f"{self.nombre} se registró correctamente."

    def iniciar_sesion(self, contrasena):
        intento = hashlib.pbkdf2_hmac(
            "sha256", contrasena.encode("utf-8"), self._sal, 100_000
        )
        self.autenticado = self.registrado and hmac.compare_digest(
            self._contrasena_hash, intento
        )
        return self.autenticado


class Estudiante(Usuario):
    def __init__(self, nombre, email, contrasena, regla_prioridad=None):
        super().__init__(nombre, email, contrasena)
        self.reservas = []
        self.no_shows = []
        self.suspensiones = []
        self.regla_prioridad = regla_prioridad or SinPrioridad()
        self._lock = RLock()

    def esta_suspendido(self, momento):
        if isinstance(momento, date) and not isinstance(momento, datetime):
            momento = datetime.combine(momento, datetime.min.time())
        with self._lock:
            return any(suspension.esta_vigente(momento) for suspension in self.suspensiones)

    def puede_reservar(self, inicio, momento=None):
        momento = momento or datetime.now()
        if self.esta_suspendido(momento):
            return False, "El solicitante está suspendido."
        return True, "Puede reservar."

    def registrar_no_show(self, fecha):
        if isinstance(fecha, date) and not isinstance(fecha, datetime):
            fecha = datetime.combine(fecha, datetime.min.time())
        with self._lock:
            self.no_shows.append(fecha)
            no_shows_del_mes = [
                no_show for no_show in self.no_shows
                if no_show.year == fecha.year and no_show.month == fecha.month
            ]
            config = ConfiguracionTecnologia.obtener_instancia()
            if len(no_shows_del_mes) == config.no_shows_para_suspension:
                suspension = Suspension(fecha, config.dias_suspension)
                self.suspensiones.append(suspension)
                return suspension
            return None


class Capitan(Estudiante):
    def __init__(self, nombre, email, contrasena, equipo):
        super().__init__(nombre, email, contrasena, PrioridadAntes18())
        self.equipo = equipo

    @classmethod
    def desde_estudiante(cls, estudiante, equipo):
        # Conserva la identidad: sus reservas existentes siguen apuntando
        # al mismo solicitante después de recibir el rol de capitán.
        estudiante.__class__ = cls
        estudiante.regla_prioridad = PrioridadAntes18()
        estudiante.equipo = equipo
        return estudiante


class Administrador(Usuario):
    def __init__(self, nombre, email, contrasena):
        super().__init__(nombre, email, contrasena)
        self.acciones = []

    def registrar_accion(self, accion, detalle, momento=None):
        self.acciones.append((momento or datetime.now(), accion, detalle))

    def gestionar_horarios(self, cancha, fecha, hora_inicio, hora_fin):
        if not self.autenticado or hora_inicio >= hora_fin:
            return None
        disponibilidad = Disponibilidad(fecha, hora_inicio, hora_fin)
        cancha.agregar_disponibilidad(disponibilidad)
        self.registrar_accion("gestionar horario", (cancha.nombre, fecha, hora_inicio, hora_fin))
        return disponibilidad

    def mover_reserva(self, reserva, nueva_disponibilidad, nuevo_inicio, nuevo_fin, momento):
        if not self.autenticado:
            return False, "Se requiere un administrador autenticado."
        cancha = reserva.cancha
        with cancha._lock:
            if reserva.estado != Reserva.ACTIVA:
                return False, "Solo se pueden mover reservas activas."
            if (nueva_disponibilidad not in cancha.disponibilidades
                    or nueva_disponibilidad.fecha != nuevo_inicio.date()
                    or nueva_disponibilidad.hora_inicio != nuevo_inicio.time()
                    or nueva_disponibilidad.hora_fin != nuevo_fin.time()):
                return False, "El nuevo horario no pertenece a la cancha."
            conflicto = any(
                horario.reserva not in (None, reserva)
                and horario.reserva.estado == Reserva.ACTIVA
                and horario.fecha == nuevo_inicio.date()
                and horario.hora_inicio < nuevo_fin.time()
                and nuevo_inicio.time() < horario.hora_fin
                for horario in cancha.disponibilidades
            )
            if (not cancha.esta_habilitada() or conflicto
                    or cancha.tiene_bloqueo_en(
                        nuevo_inicio.date(), nuevo_inicio.time(), nuevo_fin.time()
                    ) or not nueva_disponibilidad.bloquear(momento)):
                return False, "El nuevo horario no está disponible."
            reserva.disponibilidad.liberar()
            reserva.disponibilidad = nueva_disponibilidad
            reserva.inicio = nuevo_inicio
            reserva.fin = nuevo_fin
            nueva_disponibilidad.confirmar_reserva(reserva)
        self.registrar_accion(
            "mover reserva", f"{cancha.nombre}: {nuevo_inicio}", momento
        )
        return True, "Reserva movida."

    def cancelar_reserva(self, reserva, momento, facade):
        # La Facade aplica la anulación, registra la acción y notifica por sede.
        return facade.cancelar(reserva, momento, administrador=self)

    def asignar_prioridad(self, estudiante, equipo):
        if not self.autenticado or not estudiante.registrado:
            return None
        if isinstance(estudiante, Capitan):
            estudiante.equipo = equipo
            estudiante.regla_prioridad = PrioridadAntes18()
            self.registrar_accion("asignar prioridad", estudiante.email)
            return estudiante
        capitan = Capitan.desde_estudiante(estudiante, equipo)
        self.registrar_accion("asignar prioridad", capitan.email)
        return capitan


class Cancha:
    def __init__(self, nombre, tipo, habilitada=True, sede=None):
        self.nombre = nombre
        self.tipo = tipo
        self.habilitada = habilitada
        self.sede = sede
        self.disponibilidades = []
        self.bloqueos = []
        self._lock = RLock()

    def esta_habilitada(self):
        return self.habilitada

    def agregar_disponibilidad(self, disponibilidad):
        with self._lock:
            self.disponibilidades.append(disponibilidad)

    def tiene_reserva_en(self, fecha, hora_inicio, hora_fin):
        return any(
            horario.fecha == fecha and horario.reserva is not None
            and horario.reserva.estado == Reserva.ACTIVA
            and horario.hora_inicio < hora_fin and hora_inicio < horario.hora_fin
            for horario in self.disponibilidades
        )

    def tiene_bloqueo_en(self, fecha, hora_inicio, hora_fin):
        return any(
            bloqueo.fecha == fecha
            and bloqueo.hora_inicio < hora_fin and hora_inicio < bloqueo.hora_fin
            for bloqueo in self.bloqueos
        )


class Disponibilidad:
    LIMITE_PROCESO = timedelta(minutes=15)

    def __init__(self, fecha, hora_inicio, hora_fin, disponible=True):
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.disponible = disponible
        self.reserva = None
        self.bloqueada_en = None
        self._lock = Lock()

    def esta_disponible(self, momento=None):
        with self._lock:
            return self._esta_disponible(momento)

    def _esta_disponible(self, momento=None):
        if self.reserva is not None:
            return False
        if self.bloqueada_en is not None:
            if momento is not None and momento - self.bloqueada_en > self.LIMITE_PROCESO:
                self.disponible = True
                self.reserva = None
                self.bloqueada_en = None
            else:
                return False
        return self.disponible

    def bloquear(self, momento):
        with self._lock:
            if not self._esta_disponible(momento):
                return False
            self.disponible = False
            self.bloqueada_en = momento
            return True

    def confirmar_si_disponible(self, reserva, momento):
        with self._lock:
            if not self._esta_disponible(momento):
                return False
            self.disponible = False
            self.reserva = reserva
            self.bloqueada_en = None
            return True

    @staticmethod
    def confirmar_varias(asignaciones, momento):
        horarios = [disponibilidad for disponibilidad, _ in asignaciones]
        with ExitStack() as locks:
            for horario in sorted(horarios, key=id):
                locks.enter_context(horario._lock)
            for indice, (horario, _) in enumerate(asignaciones):
                if not horario._esta_disponible(momento):
                    return False, indice
            for horario, reserva in asignaciones:
                horario.disponible = False
                horario.reserva = reserva
                horario.bloqueada_en = None
        return True, None

    def confirmar_reserva(self, reserva):
        with self._lock:
            self.reserva = reserva
            self.bloqueada_en = None

    def bloquear_por_evento(self):
        with self._lock:
            self.disponible = False
            self.bloqueada_en = None

    def liberar(self):
        with self._lock:
            self.disponible = True
            self.reserva = None
            self.bloqueada_en = None


class Reserva:
    ACTIVA = "ACTIVA"
    CANCELADA = "CANCELADA"
    NO_SHOW = "NO_SHOW"
    ANULADA = "ANULADA"

    def __init__(self, solicitante, cancha, disponibilidad, inicio, fin,
                 estrategia_cancelacion, fecha_creacion=None):
        self.solicitante = solicitante
        self.estudiante = solicitante
        self.cancha = cancha
        self.disponibilidad = disponibilidad
        self.inicio = inicio
        self.fin = fin
        self.estado = self.ACTIVA
        self.estrategia_cancelacion = estrategia_cancelacion
        self.fecha_creacion = fecha_creacion or datetime.now()
        self.fecha_cancelacion = None
        self.fecha_no_show = None
        self.fecha_anulacion = None
        self.motivo_anulacion = None

    def cancelar(self, momento, estrategia=None):
        politica = estrategia or self.estrategia_cancelacion
        return politica.cancelar(self, momento)

    def cancelar_sin_penalidad(self, momento=None):
        if self.estado != self.ACTIVA:
            return False
        self.estado = self.CANCELADA
        self.fecha_cancelacion = momento or datetime.now()
        self.disponibilidad.liberar()
        return True

    def marcar_no_show(self, momento=None):
        if self.estado != self.ACTIVA:
            return False
        self.estado = self.NO_SHOW
        self.fecha_no_show = momento or datetime.now()
        self.disponibilidad.liberar()
        return True

    def anular_por_administrador(self, momento=None, motivo=""):
        if self.estado != self.ACTIVA:
            return False
        self.estado = self.ANULADA
        self.fecha_anulacion = momento or datetime.now()
        self.motivo_anulacion = motivo
        self.disponibilidad.liberar()
        return True


class ReservaRegular(Reserva):
    pass


class ReservaEquipoOficial(Reserva):
    def __init__(self, solicitante, cancha, disponibilidad, inicio, fin,
                 estrategia_cancelacion):
        super().__init__(solicitante, cancha, disponibilidad, inicio, fin,
                         estrategia_cancelacion)
        self.equipo = solicitante.equipo


class Suspension:
    def __init__(self, inicio, dias):
        self.inicio = inicio
        self.fin = inicio + timedelta(days=dias)

    def esta_vigente(self, momento):
        return self.inicio <= momento < self.fin
