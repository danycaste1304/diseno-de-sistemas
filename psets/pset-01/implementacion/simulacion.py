from datetime import date, datetime, time, timedelta

from administrador import Administrador
from cancha import Cancha
from disponibilidad import Disponibilidad
from estudiante import Capitan, Estudiante


def crear_horario(cancha, fecha, hora_inicio, hora_fin):
    horario = Disponibilidad(fecha, hora_inicio, hora_fin)
    cancha.agregar_disponibilidad(horario)
    return horario


def mostrar(numero, mensaje):
    print(f"{numero}. {mensaje}")


def main():
    fecha = date(2026, 10, 5)
    cancha = Cancha("Cancha Central", "fútbol")
    regular = Estudiante("Ana", "ana@usfq.edu.ec", "clave-segura")
    capitan = Capitan("Luis", "luis@usfq.edu.ec", "clave-capitan", "Tigres")

    # 1 a 3: cuenta de usuario.
    mostrar(1, regular.registrarse())
    mostrar(2, "Inicio de sesión exitoso." if regular.iniciar_sesion("clave-segura") else "Inicio de sesión fallido.")
    mostrar(3, "Inicio de sesión exitoso." if regular.iniciar_sesion("incorrecta") else "Inicio de sesión fallido.")

    horario_tarde = crear_horario(cancha, fecha, time(19), time(20))
    mostrar(4, f"Consulta de disponibilidad: 19:00 disponible = {horario_tarde.esta_disponible()}.")

    inicio_tarde = datetime.combine(fecha, time(19))
    reserva_regular, mensaje = regular.reservar_cancha(
        cancha, horario_tarde, inicio_tarde, inicio_tarde + timedelta(hours=1)
    )
    mostrar(5, f"Reserva regular después de las 18:00: {mensaje}")

    horario_manana = crear_horario(cancha, fecha, time(10), time(11))
    inicio_manana = datetime.combine(fecha, time(10))
    _, mensaje = regular.reservar_cancha(
        cancha, horario_manana, inicio_manana, inicio_manana + timedelta(hours=1)
    )
    mostrar(6, f"Intento regular antes de las 18:00: {mensaje}")

    reserva_capitan, mensaje = capitan.reservar_cancha(
        cancha, horario_manana, inicio_manana, inicio_manana + timedelta(hours=1)
    )
    mostrar(7, f"Reserva de capitán antes de las 18:00: {mensaje}")

    limite = Estudiante("Marta", "marta@usfq.edu.ec", "clave")
    limite.registrarse()
    for hora in (20, 21):
        horario = crear_horario(cancha, fecha, time(hora), time(hora + 1))
        inicio = datetime.combine(fecha, time(hora))
        limite.reservar_cancha(cancha, horario, inicio, inicio + timedelta(hours=1))
    tercer_horario = crear_horario(cancha, fecha, time(22), time(23))
    _, mensaje = limite.reservar_cancha(
        cancha,
        tercer_horario,
        datetime.combine(fecha, time(22)),
        datetime.combine(fecha, time(23)),
    )
    mostrar(8, f"Tercera reserva semanal: {mensaje}")

    bloqueado = Estudiante("Sofía", "sofia@usfq.edu.ec", "clave")
    bloqueado.bloqueado = True
    horario_bloqueado = crear_horario(cancha, fecha, time(18), time(19))
    _, mensaje = bloqueado.reservar_cancha(
        cancha,
        horario_bloqueado,
        datetime.combine(fecha, time(18)),
        datetime.combine(fecha, time(19)),
    )
    mostrar(9, f"Intento de estudiante bloqueado: {mensaje}")

    cancha_deshabilitada = Cancha("Cancha cerrada", "básquet", habilitada=False)
    horario_cerrado = crear_horario(cancha_deshabilitada, fecha, time(20), time(21))
    disponible = Estudiante("Diego", "diego@usfq.edu.ec", "clave")
    _, mensaje = disponible.reservar_cancha(
        cancha_deshabilitada,
        horario_cerrado,
        datetime.combine(fecha, time(20)),
        datetime.combine(fecha, time(21)),
    )
    mostrar(10, f"Cancha u horario no disponible: {mensaje}")

    cancha_auxiliar = Cancha("Cancha Auxiliar", "fútbol")
    horario_proceso = crear_horario(cancha_auxiliar, fecha, time(19), time(20))
    _, mensaje = disponible.reservar_cancha(
        cancha_auxiliar,
        horario_proceso,
        datetime.combine(fecha, time(19)),
        datetime.combine(fecha, time(20)),
        momento=datetime.combine(fecha, time(19)),
        minutos_proceso=16,
    )
    mostrar(11, f"Proceso de reserva: {mensaje} Disponible = {horario_proceso.esta_disponible()}.")

    cancelador = Estudiante("Elena", "elena@usfq.edu.ec", "clave")
    horario_cancelable = crear_horario(cancha, fecha + timedelta(days=1), time(20), time(21))
    inicio_cancelable = datetime.combine(fecha + timedelta(days=1), time(20))
    reserva_cancelable, _ = cancelador.reservar_cancha(
        cancha, horario_cancelable, inicio_cancelable, inicio_cancelable + timedelta(hours=1)
    )
    _, mensaje = cancelador.cancelar_reserva(reserva_cancelable, inicio_cancelable - timedelta(hours=2))
    mostrar(12, f"Cancelación con 2 horas de anticipación: {mensaje}")

    no_show = Estudiante("Pablo", "pablo@usfq.edu.ec", "clave")
    for indice, dia in enumerate((7, 8), start=1):
        fecha_no_show = date(2026, 10, dia)
        horario = crear_horario(cancha, fecha_no_show, time(20), time(21))
        inicio = datetime.combine(fecha_no_show, time(20))
        reserva, _ = no_show.reservar_cancha(cancha, horario, inicio, inicio + timedelta(hours=1))
        _, mensaje = no_show.cancelar_reserva(reserva, inicio - timedelta(hours=1))
        if indice == 1:
            mostrar(13, f"Cancelación tardía: {mensaje}")
        else:
            mostrar(14, f"Segundo no-show del mes: {mensaje} Bloqueado = {no_show.esta_bloqueado(fecha_no_show)}.")
    mostrar(15, f"Al iniciar noviembre, bloqueo mensual activo = {no_show.esta_bloqueado(date(2026, 11, 1))}.")

    administrador = Administrador("Carla", "carla@usfq.edu.ec", "admin")
    horario_admin = administrador.gestionar_horarios(cancha, fecha + timedelta(days=10), time(18), time(19))
    mostrar(16, f"Administrador gestiona horario: agregó {horario_admin.hora_inicio.strftime('%H:%M')}.")

    reserva_admin, _ = disponible.reservar_cancha(
        cancha,
        horario_admin,
        datetime.combine(fecha + timedelta(days=10), time(18)),
        datetime.combine(fecha + timedelta(days=10), time(19)),
    )
    nuevo_horario = administrador.gestionar_horarios(cancha, fecha + timedelta(days=10), time(19), time(20))
    nuevo_inicio = datetime.combine(fecha + timedelta(days=10), time(19))
    _, mensaje = administrador.mover_reserva(
        reserva_admin, nuevo_horario, nuevo_inicio, nuevo_inicio + timedelta(hours=1), nuevo_inicio - timedelta(days=1)
    )
    mostrar(17, f"Administrador mueve reserva: {mensaje}")
    _, mensaje = administrador.cancelar_reserva(reserva_admin)
    mostrar(18, f"Administrador cancela reserva: {mensaje}")
    administrador.bloquear_estudiante(disponible)
    mostrar(19, f"Administrador bloquea estudiante: bloqueado = {disponible.bloqueado}.")
    administrador.asignar_prioridad(regular)
    mostrar(20, f"Administrador asigna PrioridadAntes18: prioridad a las 10:00 = {regular.regla_prioridad.tiene_prioridad(time(10))}.")


if __name__ == "__main__":
    main()
