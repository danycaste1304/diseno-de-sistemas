class Estudiante:
    def __init__(self, nombre):
        self.nombre = nombre


class EquipoOficial:
    def __init__(self, nombre):
        self.nombre = nombre

class ReservaRegular:
    def __init__(self, cancha, fecha, hora_inicio, hora_fin, solicitante):
        self.cancha = cancha
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.solicitante = solicitante

    def confirmar(self):
        return "Reserva confirmada para: " + self.solicitante.nombre

class ReservaPrioridad:
    def __init__(self, cancha, fecha, hora_inicio, hora_fin, solicitante):
        self.cancha = cancha
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.solicitante = solicitante

    def confirmar(self):
        return "Reserva con prioridadconfirmada para: " + self.solicitante.nombre

'''
def reservar_desde_web(cancha, fecha, Hora_inicio, Hora_fin, Solicitante):
    if isinstance(Solicitante, EquipoOficial):
        reserva = ReservaPrioridad(cancha, fecha, Hora_inicio, Hora_fin, Solicitante)

    elif isinstance(Solicitante, Estudiante):
        reserva = ReservaRegular(cancha, fecha, Hora_inicio, Hora_fin, Solicitante)
        print ('Se creo la reserva regular con exito')

    if reserva is None:
        raise RuntimeError('No se creo con exito la reserva')
    
    return reserva
'''

def reservar_desde_hall():
    pass

class CreadorDeReserva():
    def crear_reserva(self, cancha, fecha, hora_inicio, hora_fin, solicitante):
        raise NotImplementedError

class CreadorDeReservaRegular(CreadorDeReserva):
    def crear_reserva(self, cancha, fecha, hora_inicio, hora_fin, solicitante):
        return ReservaRegular(
            cancha,
            fecha,
            hora_inicio,
            hora_fin,
            solicitante
        ) 

class CreadorDeReservaPrioritaria(CreadorDeReserva):
    def crear_reserva(self, cancha, fecha, hora_inicio, hora_fin, solicitante):
        return ReservaPrioridad(
            cancha,
            fecha,
            hora_inicio,
            hora_fin,
            solicitante
            ) 
    
class FabricaDeReservas():
    @staticmethod
    def elegir_creador(solicitante):
        if isinstance(solicitante, Estudiante):
            return CreadorDeReservaRegular()
        elif isinstance(solicitante, EquipoOficial):
            return CreadorDeReservaPrioritaria()

def reservar_desde_web(cancha, fecha, hora_inicio, hora_fin, solicitante):
    creador = FabricaDeReservas.elegir_creador(solicitante)
    reserva = creador.crear_reserva(
        cancha,
        fecha,
        hora_inicio,
        hora_fin,
        solicitante
    )

    return reserva


def main():
    reserva_1 = reservar_desde_web(
        "Cancha de futbol",
        '2026-09-07',
        '18:00',
        '20:00',
        Estudiante('daniela')
    )

    print(reserva_1.confirmar())

    reserva_2 = reservar_desde_web(
        "Cancha de futbol",
        '2026-09-07',
        '18:00',
        '20:00',
        EquipoOficial('equipo de daniela')
    )
    print(reserva_2.confirmar())

if __name__ == "__main__":
    main()


