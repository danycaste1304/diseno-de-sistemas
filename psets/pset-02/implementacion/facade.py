from contextlib import ExitStack
from datetime import datetime, timedelta

from modelos import Administrador, Capitan, Disponibilidad, Reserva
from patrones import FabricaReservas
from reglas import CancelacionAdministrativa, ConfiguracionTecnologia


class Calendario:
    def __init__(self):
        self.reservas = []
        self.bloqueos = []

    def agregar_reserva(self, reserva):
        self.reservas.append(reserva)

    def agregar_bloqueo(self, bloqueo):
        self.bloqueos.append(bloqueo)


class RegistroNoShows:
    def __init__(self):
        self.registros = []

    def registrar(self, solicitante, momento):
        suspension = solicitante.registrar_no_show(momento)
        self.registros.append((solicitante, momento))
        return suspension


class RegistroAdministrativo:
    def __init__(self):
        self.registros = []

    def registrar(self, momento, accion, detalle, administrador):
        self.registros.append((momento, accion, detalle, administrador))


class ReservaFacade:
    def __init__(self, fabrica_sede, calendario=None):
        self.servicios_sede = fabrica_sede.crear_servicios()
        self.sede = fabrica_sede.nombre_sede
        self.calendario = calendario or Calendario()
        self.registro_no_shows = RegistroNoShows()
        self.registro_administrativo = RegistroAdministrativo()

    def reservar(self, solicitante, cancha, disponibilidad, inicio, fin, momento=None,
                 minutos_proceso=0, seleccion_en=None):
        momento = momento or datetime.now()
        if seleccion_en is not None:
            minutos_proceso = (momento - seleccion_en).total_seconds() / 60
        if minutos_proceso > 15:
            # Libera una selección temporal que haya vencido.
            disponibilidad.esta_disponible(momento)
            return None, "El proceso excedió 15 minutos; no se registró la reserva."
        if not solicitante.autenticado:
            return None, "El solicitante debe iniciar sesión."
        if solicitante.esta_suspendido(momento):
            return None, "El solicitante está suspendido."
        if not cancha.esta_habilitada():
            return None, "La cancha no está habilitada."
        if cancha.sede is not None and cancha.sede != self.sede:
            return None, "La cancha pertenece a otra sede."
        if disponibilidad not in cancha.disponibilidades:
            return None, "El horario no pertenece a la cancha."
        if (disponibilidad.fecha != inicio.date()
                or disponibilidad.hora_inicio != inicio.time()
                or disponibilidad.hora_fin != fin.time()):
            return None, "La solicitud no coincide con la franja seleccionada."
        if not self.servicios_sede.validador.validar(inicio.time(), fin.time()):
            return None, "El horario no cumple las reglas de la sede."
        permitido, mensaje = solicitante.puede_reservar(inicio, momento)
        if not permitido:
            return None, mensaje

        with cancha._lock, solicitante._lock:
            if solicitante.esta_suspendido(momento):
                return None, "El solicitante está suspendido."
            if cancha.sede is None:
                cancha.sede = self.sede
            elif cancha.sede != self.sede:
                return None, "La cancha pertenece a otra sede."
            if (cancha.tiene_bloqueo_en(inicio.date(), inicio.time(), fin.time())
                    or cancha.tiene_reserva_en(inicio.date(), inicio.time(), fin.time())):
                return None, "El horario no está disponible."
            reserva = FabricaReservas.crear_reserva(
                solicitante, cancha, disponibilidad, inicio, fin
            )
            reserva.fecha_creacion = momento
            if not disponibilidad.confirmar_si_disponible(reserva, momento):
                return None, "El horario no está disponible."
            solicitante.reservas.append(reserva)
            self.calendario.agregar_reserva(reserva)
        self.servicios_sede.notificador.notificar(solicitante, "Reserva confirmada.")
        return reserva, "Reserva confirmada."

    def reservar_en_competencia(self, solicitudes):
        """Arbitra solicitudes recibidas juntas para una misma cancha y franja."""
        if not solicitudes:
            return []
        cancha = solicitudes[0][1]
        inicio = solicitudes[0][3]
        fin = solicitudes[0][4]
        if any(s[1] is not cancha or s[3] != inicio or s[4] != fin for s in solicitudes):
            raise ValueError("Las solicitudes en competencia deben tener la misma cancha y franja.")
        resultados = [None] * len(solicitudes)
        orden = sorted(
            enumerate(solicitudes),
            key=lambda item: item[1][0].regla_prioridad.tiene_prioridad(item[1][5]),
            reverse=True,
        )
        with cancha._lock:
            ganador_prioritario = False
            for indice, solicitud in orden:
                if ganador_prioritario and not solicitud[0].regla_prioridad.tiene_prioridad(solicitud[5]):
                    resultados[indice] = (
                        None, "La solicitud regular perdió prioridad ante una solicitud de capitán."
                    )
                    continue
                resultados[indice] = self.reservar(*solicitud[:5], momento=solicitud[5])
                if resultados[indice][0] is not None:
                    ganador_prioritario = solicitud[0].regla_prioridad.tiene_prioridad(solicitud[5])
        return resultados

    def reservar_recurrente(self, solicitud, momento=None, paso=None):
        momento = momento or datetime.now()
        semanas = solicitud.numero_semanas
        if not 2 <= semanas <= 8:
            return [], "El número de semanas debe estar entre 2 y 8."
        if not isinstance(solicitud.solicitante, Capitan):
            return [], "Solo un capitán puede solicitar una reserva recurrente."
        if not solicitud.solicitante.autenticado:
            return [], "El solicitante debe iniciar sesión."
        if solicitud.solicitante.esta_suspendido(momento):
            return [], "El solicitante está suspendido."
        cancha = solicitud.cancha
        if not cancha.esta_habilitada():
            return [], "La cancha no está habilitada."
        if cancha.sede is not None and cancha.sede != self.sede:
            return [], "La cancha pertenece a otra sede."

        hora_inicio, hora_fin = solicitud.franja
        if paso:
            paso(f"Se generan {semanas} fechas semanales tentativas.")
        with cancha._lock, solicitud.solicitante._lock:
            if solicitud.solicitante.esta_suspendido(momento):
                return [], "El solicitante está suspendido."
            if cancha.sede is None:
                cancha.sede = self.sede
            elif cancha.sede != self.sede:
                return [], "La cancha pertenece a otra sede."
            horarios = []
            inicios = []
            for indice in range(semanas):
                fecha = solicitud.fecha_inicio + timedelta(weeks=indice)
                inicio = datetime.combine(fecha, hora_inicio)
                fin = datetime.combine(fecha, hora_fin)
                disponibilidad = next((horario for horario in cancha.disponibilidades
                    if horario.fecha == fecha and horario.hora_inicio == hora_inicio
                    and horario.hora_fin == hora_fin), None)
                if disponibilidad is None:
                    if paso:
                        paso(f"Semana {indice + 1}: no existe la franja solicitada.")
                    return [], f"Conflicto en la semana {indice + 1}: no existe una franja disponible."
                if not self.servicios_sede.validador.validar(hora_inicio, hora_fin):
                    return [], f"La serie excede el horario permitido por la sede en la semana {indice + 1}."
                if (cancha.tiene_bloqueo_en(fecha, hora_inicio, hora_fin)
                        or cancha.tiene_reserva_en(fecha, hora_inicio, hora_fin)):
                    if paso:
                        paso(f"Semana {indice + 1}: la franja presenta un conflicto.")
                    return [], f"Conflicto en la semana {indice + 1}; no se registró ninguna reserva."
                if not disponibilidad.esta_disponible(momento):
                    if paso:
                        paso(f"Semana {indice + 1}: la franja no está disponible.")
                    return [], f"Conflicto en la semana {indice + 1}; no se registró ninguna reserva."
                permitido, mensaje = solicitud.solicitante.puede_reservar(inicio, momento)
                if not permitido:
                    return [], f"La serie no cumple las reglas en la semana {indice + 1}: {mensaje}"
                horarios.append(disponibilidad)
                inicios.append((inicio, fin))
                if paso:
                    paso(f"Semana {indice + 1}: sede, suspensión, prioridad y disponibilidad válidas.")

            reservas = []
            for disponibilidad, (inicio, fin) in zip(horarios, inicios):
                reserva = FabricaReservas.crear_reserva(
                    solicitud.solicitante, cancha, disponibilidad, inicio, fin
                )
                reserva.fecha_creacion = momento
                reserva.equipo_prestado = (
                    list(solicitud.equipo_prestado)
                    if solicitud.equipo_prestado is not None else None
                )
                reserva.notas = solicitud.notas
                reservas.append(reserva)
            confirmadas, semana_conflicto = Disponibilidad.confirmar_varias(
                list(zip(horarios, reservas)), momento
            )
            if not confirmadas:
                return [], f"Conflicto en la semana {semana_conflicto + 1}; no se registró ninguna reserva."

            solicitud.solicitante.reservas.extend(reservas)
            for reserva in reservas:
                self.calendario.agregar_reserva(reserva)
            if paso:
                paso("Se confirma toda la serie de forma atómica y se guardan equipo y notas.")
        self.servicios_sede.notificador.notificar(
            solicitud.solicitante,
            f"Reserva recurrente confirmada para {semanas} semanas."
        )
        return reservas, f"Se confirmaron {semanas} reservas recurrentes."

    def cancelar(self, reserva, momento, solicitante=None, administrador=None,
                 motivo=""):
        cancha = reserva.cancha
        with cancha._lock:
            if cancha.sede != self.sede:
                return False, "La reserva pertenece a otra sede."
            if reserva.estado != Reserva.ACTIVA:
                return False, "La reserva ya no está activa."
            if administrador is not None:
                if not isinstance(administrador, Administrador) or not administrador.autenticado:
                    return False, "Se requiere un administrador autenticado."
                resultado, mensaje = CancelacionAdministrativa().cancelar(
                    reserva, momento, motivo
                )
                if resultado:
                    self.registro_administrativo.registrar(
                        momento, "anular reserva", motivo, administrador.email
                    )
                    administrador.registrar_accion(
                        "anular reserva", f"{cancha.nombre}: {reserva.inicio}", momento
                    )
            else:
                if solicitante is not reserva.solicitante:
                    return False, "Solo el solicitante puede cancelar su reserva."
                if not solicitante.autenticado:
                    return False, "El solicitante debe iniciar sesión."
                if momento >= reserva.inicio:
                    return False, "La reserva ya inició y no se puede cancelar."
                resultado, mensaje = reserva.cancelar(momento)
                if reserva.estado == Reserva.NO_SHOW:
                    suspension = self.registro_no_shows.registrar(
                        reserva.solicitante, momento
                    )
                    if suspension is not None:
                        dias = ConfiguracionTecnologia.obtener_instancia().dias_suspension
                        mensaje += f" Se aplicó una suspensión de {dias} días."
        self.servicios_sede.notificador.notificar(reserva.solicitante, mensaje)
        return resultado, mensaje

    def bloquear(self, plantilla, canchas, fechas, administrador, momento=None, paso=None):
        momento = momento or datetime.now()
        if not isinstance(administrador, Administrador) or not administrador.autenticado:
            return [], "Se requiere un administrador autenticado."
        if not canchas or not fechas or plantilla.hora_inicio >= plantilla.hora_fin:
            return [], "Los datos del bloqueo no son válidos."
        if any(cancha.sede is not None and cancha.sede != self.sede for cancha in canchas):
            return [], "Todas las canchas del bloqueo deben pertenecer a la misma sede."
        if not self.servicios_sede.validador.validar(
            plantilla.hora_inicio, plantilla.hora_fin
        ):
            return [], "El horario del bloqueo no está permitido por la sede."
        if paso:
            paso("Se validan sedes, fechas y horario del bloqueo.")

        bloqueos = []
        conflictos = []
        horarios_afectados = []
        with ExitStack() as locks:
            for cancha in sorted(set(canchas), key=id):
                locks.enter_context(cancha._lock)
            for cancha in canchas:
                if cancha.sede is None:
                    cancha.sede = self.sede
                for fecha in fechas:
                    bloqueo = plantilla.clonar_para(cancha, fecha)
                    bloqueos.append(bloqueo)
                    for horario in cancha.disponibilidades:
                        se_superpone = (
                            horario.fecha == fecha
                            and horario.hora_inicio < plantilla.hora_fin
                            and plantilla.hora_inicio < horario.hora_fin
                        )
                        if se_superpone:
                            horarios_afectados.append(horario)
                            if horario.reserva is not None and horario.reserva not in conflictos:
                                conflictos.append(horario.reserva)
            if paso:
                palabra = "reserva" if len(conflictos) == 1 else "reservas"
                verbo = "encontró" if len(conflictos) == 1 else "encontraron"
                paso(f"Se clonó la plantilla {len(bloqueos)} veces y se {verbo} {len(conflictos)} {palabra} en conflicto.")

            for reserva in conflictos:
                if reserva.anular_por_administrador(momento, plantilla.motivo):
                    self.registro_administrativo.registrar(
                        momento, "anular reserva por bloqueo", plantilla.motivo,
                        administrador.email
                    )
                    administrador.registrar_accion(
                        "anular reserva por bloqueo",
                        f"{reserva.cancha.nombre}: {reserva.inicio}", momento
                    )
            if paso and conflictos:
                paso("Se anulan las reservas en conflicto sin registrar no-show.")
            for horario in horarios_afectados:
                horario.bloquear_por_evento()
            for bloqueo in bloqueos:
                horario_bloqueado = Disponibilidad(
                    bloqueo.fecha, bloqueo.hora_inicio, bloqueo.hora_fin,
                    disponible=False
                )
                horario_bloqueado.bloqueo = bloqueo
                bloqueo.cancha.agregar_disponibilidad(horario_bloqueado)
                bloqueo.cancha.bloqueos.append(bloqueo)
                self.calendario.agregar_bloqueo(bloqueo)
            if paso:
                paso("Las franjas quedan bloqueadas y la acción administrativa se registra.")
            self.registro_administrativo.registrar(
                momento, "crear bloqueo", plantilla.motivo, administrador.email
            )
            administrador.registrar_accion(
                "crear bloqueo", f"{len(bloqueos)} bloqueos: {plantilla.motivo}", momento
            )
        for reserva in conflictos:
            if reserva.estado == Reserva.ANULADA:
                self.servicios_sede.notificador.notificar(
                    reserva.solicitante,
                    f"Reserva anulada por bloqueo de evento: {plantilla.motivo}"
                )
        return bloqueos, f"Se registraron {len(bloqueos)} bloqueos."

    def consultar_disponibilidad(self, solicitante, cancha, fecha):
        if not solicitante.autenticado:
            return [], "El solicitante debe iniciar sesión."
        if cancha.sede is not None and cancha.sede != self.sede:
            return [], "La cancha pertenece a otra sede."
        with cancha._lock:
            horarios = [
                horario for horario in cancha.disponibilidades
                if horario.fecha == fecha and horario.esta_disponible()
                and not cancha.tiene_bloqueo_en(
                    fecha, horario.hora_inicio, horario.hora_fin
                )
                and not cancha.tiene_reserva_en(
                    fecha, horario.hora_inicio, horario.hora_fin
                )
                and self.servicios_sede.validador.validar(
                    horario.hora_inicio, horario.hora_fin
                )
            ]
        return horarios, "Franjas disponibles consultadas."

    def consultar_mis_reservas(self, solicitante):
        if not solicitante.autenticado:
            return [], "El solicitante debe iniciar sesión."
        return list(solicitante.reservas), "Reservas del solicitante consultadas."
