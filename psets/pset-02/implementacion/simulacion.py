from datetime import date, datetime, time, timedelta
from threading import Barrier, Lock, Thread

from facade import ReservaFacade
from modelos import Administrador, Cancha, Capitan, Disponibilidad, Estudiante
from patrones import Bloqueo, FabricaSedeNorte, FabricaSedeSur, ReservaRecurrenteBuilder, imprimir
from reglas import ConfiguracionTecnologia


def agregar_horario(cancha, fecha, hora_inicio, hora_fin):
    horario = Disponibilidad(fecha, hora_inicio, hora_fin)
    cancha.agregar_disponibilidad(horario)
    return horario


PASOS = {}


def mostrar(escenario, mensaje):
    PASOS[escenario] = PASOS.get(escenario, 0) + 1
    imprimir(f"[{escenario}.{PASOS[escenario]}] {mensaje}")


def hacer_reserva(facade, solicitante, cancha, horario, inicio, fin, momento,
                 seleccion_en=None):
    return facade.reservar(
        solicitante, cancha, horario, inicio, fin, momento=momento,
        seleccion_en=seleccion_en
    )


def registrar_y_autenticar(usuario, contrasena="clave"):
    usuario.registrarse()
    autenticado = usuario.iniciar_sesion(contrasena)
    estado = "sesión iniciada" if autenticado else "credenciales rechazadas"
    imprimir(f"[Acceso] {usuario.nombre}: registro y {estado}.")
    return autenticado


def hacer_solicitud_recurrente(facade, cancha, solicitante, fechas, franja,
                                equipo, notas, momento):
    hora_inicio, hora_fin = franja
    for fecha in fechas:
        agregar_horario(cancha, fecha, hora_inicio, hora_fin)
    solicitud = (
        ReservaRecurrenteBuilder()
        .para_cancha(cancha)
        .desde(fechas[0])
        .con_franja(hora_inicio, hora_fin)
        .solicitada_por(solicitante)
        .por_semanas(len(fechas))
        .con_equipo_prestado(equipo)
        .con_notas(notas)
        .construir()
    )
    reservas, mensaje = facade.reservar_recurrente(
        solicitud, momento, paso=lambda texto: mostrar("3", texto)
    )
    return reservas, mensaje, solicitud


def main():
    configuracion = ConfiguracionTecnologia.obtener_instancia()
    configuracion.no_shows_para_suspension = 3

    sede_norte = ReservaFacade(FabricaSedeNorte())
    sede_sur = ReservaFacade(FabricaSedeSur())

    imprimir("ReservaU — simulación de los flujos principales")

    # 1. Reserva por cada sede: solicitud, validación, confirmación y aviso.
    fecha = date(2026, 9, 1)
    estudiante_norte = Estudiante("Ana", "ana@usfq.edu.ec", "clave")
    estudiante_sur = Estudiante("Diego", "diego@usfq.edu.ec", "clave")
    cancha_norte = Cancha("Cancha Norte 1", "fútbol", sede="Norte")
    cancha_sur = Cancha("Cancha Sur 1", "fútbol", sede="Sur")
    registrar_y_autenticar(estudiante_norte)
    registrar_y_autenticar(estudiante_sur)

    mostrar("1", "Norte: el estudiante selecciona cancha y franja 19:00–20:00.")
    horario_norte = agregar_horario(cancha_norte, fecha, time(19), time(20))
    inicio_norte = datetime.combine(fecha, time(19))
    mostrar("1", "Norte: la Facade valida reglas, horario y disponibilidad.")
    reserva_norte, mensaje = hacer_reserva(
        sede_norte, estudiante_norte, cancha_norte, horario_norte,
        inicio_norte, inicio_norte + timedelta(hours=1),
        inicio_norte - timedelta(days=1)
    )
    mostrar("1", f"Norte: resultado: {mensaje}")

    mostrar("1", "Sur: el estudiante selecciona cancha y franja 21:00–22:00.")
    horario_sur = agregar_horario(cancha_sur, fecha, time(21), time(22))
    inicio_sur = datetime.combine(fecha, time(21))
    mostrar("1", "Sur: la Facade valida reglas, horario y disponibilidad.")
    reserva_sur, mensaje = hacer_reserva(
        sede_sur, estudiante_sur, cancha_sur, horario_sur,
        inicio_sur, inicio_sur + timedelta(hours=1),
        inicio_sur - timedelta(days=1)
    )
    mostrar("1", f"Sur: resultado: {mensaje}")

    # 2. La sede Norte cierra a las 22:00; la solicitud se rechaza antes de
    # confirmar y no se envía una notificación de reserva.
    mostrar("2", "El solicitante pide en Norte una franja de 23:00–23:59.")
    horario_fuera = agregar_horario(cancha_norte, fecha, time(23), time(23, 59))
    inicio_fuera = datetime.combine(fecha, time(23))
    _, mensaje = hacer_reserva(
        sede_norte, estudiante_norte, cancha_norte, horario_fuera,
        inicio_fuera, datetime.combine(fecha, time(23, 59)),
        inicio_fuera - timedelta(days=1)
    )
    mostrar("2", f"La sede rechaza la solicitud: {mensaje}")

    mostrar("2", "Un estudiante regular puede reservar a las 10:00 si no compite con otra solicitud.")
    cancha_prioridad_libre = Cancha("Cancha Norte 8", "fútbol", sede="Norte")
    horario_prioridad_libre = agregar_horario(
        cancha_prioridad_libre, fecha, time(10), time(11)
    )
    inicio_prioridad = datetime.combine(fecha, time(10))
    regular_temprano = Estudiante("Elena", "elena@usfq.edu.ec", "clave")
    registrar_y_autenticar(regular_temprano)
    _, mensaje = hacer_reserva(
        sede_norte, regular_temprano, cancha_prioridad_libre,
        horario_prioridad_libre, inicio_prioridad,
        inicio_prioridad + timedelta(hours=1), inicio_prioridad - timedelta(days=1)
    )
    mostrar("2", f"Sin conflicto antes de las 18:00: {mensaje}")

    mostrar("2", "En una competencia antes de las 18:00, el capitán tiene prioridad.")
    cancha_prioridad = Cancha("Cancha Norte 9", "fútbol", sede="Norte")
    horario_prioridad = agregar_horario(cancha_prioridad, fecha, time(11), time(12))
    inicio_prioridad = datetime.combine(fecha, time(11))
    regular_en_conflicto = Estudiante("Julia", "julia@usfq.edu.ec", "clave")
    capitan_prioridad = Capitan("Raúl", "raul@usfq.edu.ec", "clave", "Cóndores")
    registrar_y_autenticar(regular_en_conflicto)
    registrar_y_autenticar(capitan_prioridad)
    resultados_prioridad = sede_norte.reservar_en_competencia([
        (regular_en_conflicto, cancha_prioridad, horario_prioridad,
         inicio_prioridad, inicio_prioridad + timedelta(hours=1),
         inicio_prioridad - timedelta(days=1)),
        (capitan_prioridad, cancha_prioridad, horario_prioridad,
         inicio_prioridad, inicio_prioridad + timedelta(hours=1),
         inicio_prioridad - timedelta(days=1)),
    ])
    mostrar("2", f"Solicitud regular en conflicto: {resultados_prioridad[0][1]}")
    mostrar("2", f"Solicitud de capitán priorizada: {resultados_prioridad[1][1]}")

    mostrar("2", "Después de las 18:00, ambas solicitudes tienen igual prioridad.")
    fecha_sin_prioridad = fecha + timedelta(days=1)
    cancha_sin_prioridad = Cancha("Cancha Norte 10", "fútbol", sede="Norte")
    horario_sin_prioridad = agregar_horario(
        cancha_sin_prioridad, fecha_sin_prioridad, time(10), time(11)
    )
    inicio_sin_prioridad = datetime.combine(fecha_sin_prioridad, time(10))
    momento_tarde = datetime.combine(fecha, time(19))
    resultados_sin_prioridad = sede_norte.reservar_en_competencia([
        (regular_en_conflicto, cancha_sin_prioridad, horario_sin_prioridad,
         inicio_sin_prioridad, inicio_sin_prioridad + timedelta(hours=1), momento_tarde),
        (capitan_prioridad, cancha_sin_prioridad, horario_sin_prioridad,
         inicio_sin_prioridad, inicio_sin_prioridad + timedelta(hours=1), momento_tarde),
    ])
    mostrar("2", f"Primera solicitud válida (estudiante): {resultados_sin_prioridad[0][1]}")
    mostrar("2", f"Solicitud posterior (capitán): {resultados_sin_prioridad[1][1]}")

    mostrar("2", "Una selección que tarda 16 minutos debe vencer sin crear reserva.")
    cancha_vencida = Cancha("Cancha Norte 11", "fútbol", sede="Norte")
    horario_vencido = agregar_horario(cancha_vencida, fecha, time(20), time(21))
    inicio_vencido = datetime.combine(fecha, time(20))
    seleccion_en = datetime.combine(fecha, time(12))
    _, mensaje = hacer_reserva(
        sede_norte, regular_en_conflicto, cancha_vencida, horario_vencido,
        inicio_vencido, inicio_vencido + timedelta(hours=1),
        seleccion_en + timedelta(minutes=16), seleccion_en=seleccion_en
    )
    mostrar("2", f"Proceso vencido: {mensaje}")

    # 3. Primero se confirma una serie de tres semanas; después se intenta
    # otra serie cuya primera semana ya está ocupada.
    mostrar("3", "El capitán solicita una serie recurrente de tres semanas.")
    cancha_recurrente = Cancha("Cancha Norte 2", "fútbol", sede="Norte")
    fechas_recurrentes = [fecha + timedelta(days=1 + 7 * semana) for semana in range(3)]
    capitan_recurrente = Capitan("Luis", "luis@usfq.edu.ec", "clave", "Tigres")
    registrar_y_autenticar(capitan_recurrente)
    recurrentes, mensaje, _ = hacer_solicitud_recurrente(
        sede_norte, cancha_recurrente,
        capitan_recurrente,
        fechas_recurrentes, (time(19), time(20)), ["balón"],
        "Práctica semanal", datetime(2026, 8, 31, 9)
    )
    mostrar("3", f"Resultado de la serie: {mensaje}")

    cancha_conflicto = Cancha("Cancha Norte 3", "básquet", sede="Norte")
    fechas_conflicto = [fecha + timedelta(days=28 + 7 * semana) for semana in range(3)]
    solicitante_conflicto = Capitan("Marta", "marta@usfq.edu.ec", "clave", "Pumas")
    registrar_y_autenticar(solicitante_conflicto)
    horario_ocupado = agregar_horario(
        cancha_conflicto, fechas_conflicto[0], time(18), time(19)
    )
    inicio_ocupado = datetime.combine(fechas_conflicto[0], time(18))
    mostrar("3", "Se ocupa previamente la franja de la primera semana de la serie siguiente.")
    hacer_reserva(
        sede_norte, estudiante_sur, cancha_conflicto, horario_ocupado,
        inicio_ocupado, inicio_ocupado + timedelta(hours=1),
        inicio_ocupado - timedelta(days=1)
    )
    _, mensaje, _ = hacer_solicitud_recurrente(
        sede_norte, cancha_conflicto, solicitante_conflicto,
        fechas_conflicto, (time(18), time(19)), None,
        "Serie con conflicto", inicio_ocupado - timedelta(days=1)
    )
    mostrar(
        "3",
        f"Serie rechazada en la semana 1 de {len(fechas_conflicto)} "
        f"({fechas_conflicto[0]}): {mensaje}"
    )

    # 4. Las políticas de cancelación producen tres desenlaces distintos.
    mostrar("4", "Se crea una reserva regular para la estudiante.")
    horario_cancelar = agregar_horario(cancha_norte, fecha, time(20), time(21))
    inicio_cancelar = datetime.combine(fecha, time(20))
    reserva_estudiante, _ = hacer_reserva(
        sede_norte, estudiante_norte, cancha_norte, horario_cancelar,
        inicio_cancelar, inicio_cancelar + timedelta(hours=1),
        inicio_cancelar - timedelta(days=1)
    )
    mostrar("4", "La estudiante solicita cancelar con dos horas de anticipación.")
    _, mensaje = sede_norte.cancelar(
        reserva_estudiante, inicio_cancelar - timedelta(hours=2),
        solicitante=estudiante_norte
    )
    mostrar("4", f"Estudiante: {mensaje}")

    mostrar("4", "El capitán solicita cancelar con 23 horas de anticipación.")
    inicio_capitan = datetime.combine(fechas_recurrentes[0], time(19))
    _, mensaje = sede_norte.cancelar(
        recurrentes[0], inicio_capitan - timedelta(hours=23),
        solicitante=capitan_recurrente
    )
    mostrar("4", f"Capitán: {mensaje}")

    mostrar("4", "Se crea una reserva que luego deberá anular el administrador.")
    horario_admin = agregar_horario(cancha_sur, fecha, time(18), time(19))
    inicio_admin = datetime.combine(fecha, time(18))
    reserva_admin, _ = hacer_reserva(
        sede_sur, estudiante_sur, cancha_sur, horario_admin,
        inicio_admin, inicio_admin + timedelta(hours=1),
        inicio_admin - timedelta(days=2)
    )
    administrador = Administrador("Admin", "admin@usfq.edu.ec", "clave")
    registrar_y_autenticar(administrador)
    mostrar("4", "El administrador anula la reserva sin penalidad.")
    _, mensaje = sede_sur.cancelar(
        reserva_admin, inicio_admin - timedelta(minutes=30),
        administrador=administrador, motivo="Mantenimiento institucional"
    )
    mostrar("4", f"Anulación administrativa: {mensaje}")

    # 5. Se preparan tres reservas en semanas distintas, se registran los
    # tres no-shows y luego se intenta reservar durante la suspensión.
    mostrar("5", "Un solicitante acumula tres no-shows durante septiembre.")
    solicitante_no_show = Estudiante("Pablo", "pablo@usfq.edu.ec", "clave")
    registrar_y_autenticar(solicitante_no_show)
    cancha_no_show = Cancha("Cancha Norte 4", "fútbol", sede="Norte")
    reservas_no_show = []
    fechas_no_show = [date(2026, 9, dia) for dia in (2, 9, 16)]
    for semana, fecha_no_show in enumerate(fechas_no_show, start=1):
        horario = agregar_horario(cancha_no_show, fecha_no_show, time(20), time(21))
        inicio = datetime.combine(fecha_no_show, time(20))
        mostrar("5", f"Semana {semana}: se solicita la reserva antes de la fecha de juego.")
        reserva, mensaje = hacer_reserva(
            sede_norte, solicitante_no_show, cancha_no_show, horario,
            inicio, inicio + timedelta(hours=1), inicio - timedelta(days=2)
        )
        reservas_no_show.append((reserva, inicio))
        mostrar("5", f"Semana {semana}: {mensaje}")
    for semana, (reserva, inicio) in enumerate(reservas_no_show, start=1):
        _, mensaje = sede_norte.cancelar(
            reserva, inicio - timedelta(hours=1), solicitante=solicitante_no_show
        )
        mostrar("5", f"Semana {semana}: {mensaje} No-shows acumulados = {len(solicitante_no_show.no_shows)}.")
    fecha_intento = date(2026, 9, 17)
    inicio_intento = datetime.combine(fecha_intento, time(19))
    horario_intento = agregar_horario(cancha_no_show, fecha_intento, time(19), time(20))
    _, mensaje = hacer_reserva(
        sede_norte, solicitante_no_show, cancha_no_show, horario_intento,
        inicio_intento, inicio_intento + timedelta(hours=1),
        inicio_intento - timedelta(days=1)
    )
    mostrar("5", f"Intento posterior al tercer no-show: {mensaje}")

    # 6. Se bloquean dos canchas; una tiene una reserva que se anula y notifica.
    fecha_evento = date(2026, 10, 15)
    cancha_evento_ocupada = Cancha("Cancha Norte 5", "fútbol", sede="Norte")
    cancha_evento_libre = Cancha("Cancha Norte 6", "fútbol", sede="Norte")
    horario_evento = agregar_horario(
        cancha_evento_ocupada, fecha_evento, time(18), time(20)
    )
    inicio_evento = datetime.combine(fecha_evento, time(18))
    mostrar("6", "Ya existe una reserva en la cancha que se bloqueará.")
    reserva_afectada, _ = hacer_reserva(
        sede_norte, estudiante_norte, cancha_evento_ocupada, horario_evento,
        inicio_evento, inicio_evento + timedelta(hours=2),
        inicio_evento - timedelta(days=3)
    )
    mostrar("6", "El administrador define la plantilla del evento y selecciona dos canchas.")
    plantilla = Bloqueo(time(18), time(20), ["conos", "chalecos"], "Evento universitario")
    bloqueos, mensaje_bloqueo = sede_norte.bloquear(
        plantilla, [cancha_evento_ocupada, cancha_evento_libre], [fecha_evento],
        administrador=administrador, paso=lambda texto: mostrar("6", texto)
    )
    mostrar("6", f"Resultado del bloqueo: {mensaje_bloqueo}")
    mostrar("6", f"La reserva existente terminó en estado {reserva_afectada.estado}.")
    bloqueos[0].equipo_prestado.append("balón agregado al primer clon")
    mostrar("6", f"El equipo de la plantilla permanece intacto: {plantilla.equipo_prestado}.")
    mostrar("6", f"El equipo del segundo clon permanece independiente: {bloqueos[1].equipo_prestado}.")

    # 7. Dos solicitudes salen de una barrera al mismo tiempo para la misma franja.
    imprimir("[7] Dos solicitantes intentan reservar simultáneamente la misma franja.")
    fecha_concurrente = date(2026, 10, 20)
    cancha_concurrente = Cancha("Cancha Norte 7", "fútbol", sede="Norte")
    horario_concurrente = agregar_horario(
        cancha_concurrente, fecha_concurrente, time(19), time(20)
    )
    inicio_concurrente = datetime.combine(fecha_concurrente, time(19))
    barrera = Barrier(3)
    bloqueo_print = Lock()
    resultados = []

    def solicitud_concurrente(nombre):
        solicitante = Estudiante(nombre, f"{nombre.lower()}@usfq.edu.ec", "clave")
        registrar_y_autenticar(solicitante)
        barrera.wait()
        reserva, mensaje = hacer_reserva(
            sede_norte, solicitante, cancha_concurrente, horario_concurrente,
            inicio_concurrente, inicio_concurrente + timedelta(hours=1),
            inicio_concurrente - timedelta(minutes=30)
        )
        with bloqueo_print:
            resultados.append(reserva)
            resultado = "confirmada" if reserva is not None else "rechazada"
            imprimir(f"[7] {nombre}: solicitud {resultado} ({mensaje})")

    hilos = [
        Thread(target=solicitud_concurrente, args=(nombre,))
        for nombre in ("Sofía", "Mateo")
    ]
    for hilo in hilos:
        hilo.start()
    barrera.wait()
    for hilo in hilos:
        hilo.join()
    confirmadas = sum(reserva is not None for reserva in resultados)
    imprimir(f"[7] Total de reservas confirmadas para la franja: {confirmadas}.")


if __name__ == "__main__":
    main()
