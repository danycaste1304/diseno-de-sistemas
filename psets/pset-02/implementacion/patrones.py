import copy
from abc import ABC, abstractmethod
from datetime import time
from threading import Lock
from typing import NamedTuple

from modelos import Capitan, ReservaEquipoOficial, ReservaRegular
from reglas import CancelacionCapitan, CancelacionEstudiante


_lock_salida = Lock()


def imprimir(mensaje):
    with _lock_salida:
        print(mensaje, flush=True)


# Factory Method: cada creador instancia su tipo de reserva y le asigna su política.
class CreadorDeReserva(ABC):
    @abstractmethod
    def crear_reserva(self, solicitante, cancha, disponibilidad, inicio, fin):
        pass


class CreadorReservaRegular(CreadorDeReserva):
    def crear_reserva(self, solicitante, cancha, disponibilidad, inicio, fin):
        return ReservaRegular(solicitante, cancha, disponibilidad, inicio, fin,
                              CancelacionEstudiante())


class CreadorReservaEquipoOficial(CreadorDeReserva):
    def crear_reserva(self, solicitante, cancha, disponibilidad, inicio, fin):
        return ReservaEquipoOficial(solicitante, cancha, disponibilidad, inicio, fin,
                                    CancelacionCapitan())


class FabricaReservas:
    @staticmethod
    def elegir_creador(solicitante):
        if isinstance(solicitante, Capitan):
            return CreadorReservaEquipoOficial()
        return CreadorReservaRegular()

    @staticmethod
    def crear_reserva(solicitante, cancha, disponibilidad, inicio, fin):
        creador = FabricaReservas.elegir_creador(solicitante)
        return creador.crear_reserva(solicitante, cancha, disponibilidad, inicio, fin)


# Abstract Factory: cada sede crea juntos su validador y su notificador.
class ValidadorHorario(ABC):
    @abstractmethod
    def validar(self, inicio, fin):
        pass


class Notificador(ABC):
    def __init__(self):
        self.registros = []

    @abstractmethod
    def notificar(self, solicitante, mensaje):
        pass


class ValidadorSedeNorte(ValidadorHorario):
    def validar(self, inicio, fin):
        return time(6) <= inicio < fin <= time(22)


class NotificadorSedeNorte(Notificador):
    def notificar(self, solicitante, mensaje):
        self.registros.append((solicitante.email, "correo institucional", mensaje))
        imprimir(f"[Campus Norte - correo institucional] {solicitante.nombre}: {mensaje}")


class ValidadorSedeSur(ValidadorHorario):
    def validar(self, inicio, fin):
        return time(7) <= inicio < fin <= time(23)


class NotificadorSedeSur(Notificador):
    def notificar(self, solicitante, mensaje):
        self.registros.append((solicitante.email, "mensaje de texto", mensaje))
        imprimir(f"[Campus Sur - mensaje de texto] {solicitante.nombre}: {mensaje}")


class ServiciosSede(NamedTuple):
    validador: ValidadorHorario
    notificador: Notificador


class FabricaSede(ABC):
    @property
    @abstractmethod
    def nombre_sede(self):
        pass

    @abstractmethod
    def crear_servicios(self):
        pass


class FabricaSedeNorte(FabricaSede):
    nombre_sede = "Norte"

    def crear_servicios(self):
        return ServiciosSede(ValidadorSedeNorte(), NotificadorSedeNorte())


class FabricaSedeSur(FabricaSede):
    nombre_sede = "Sur"

    def crear_servicios(self):
        return ServiciosSede(ValidadorSedeSur(), NotificadorSedeSur())


# Builder: los cuatro datos de la solicitud son obligatorios; los demás son opcionales.
class ReservaRecurrente:
    def __init__(self, cancha, fecha_inicio, franja, solicitante,
                 numero_semanas=2, equipo_prestado=None, notas=""):
        self.cancha = cancha
        self.fecha_inicio = fecha_inicio
        self.franja = franja
        self.solicitante = solicitante
        self.numero_semanas = numero_semanas
        self.equipo_prestado = equipo_prestado
        self.notas = notas


class ReservaRecurrenteBuilder:
    def __init__(self):
        self.cancha = None
        self.fecha_inicio = None
        self.franja = None
        self.solicitante = None
        self.numero_semanas = 2
        self.equipo_prestado = None
        self.notas = ""

    def para_cancha(self, cancha):
        self.cancha = cancha
        return self

    def desde(self, fecha_inicio):
        self.fecha_inicio = fecha_inicio
        return self

    def con_franja(self, hora_inicio, hora_fin):
        self.franja = (hora_inicio, hora_fin)
        return self

    def solicitada_por(self, solicitante):
        self.solicitante = solicitante
        return self

    def por_semanas(self, numero_semanas):
        self.numero_semanas = numero_semanas
        return self

    def con_equipo_prestado(self, equipo):
        self.equipo_prestado = equipo
        return self

    def con_notas(self, notas):
        self.notas = notas
        return self

    def construir(self):
        if any(valor is None for valor in (
            self.cancha, self.fecha_inicio, self.franja, self.solicitante
        )):
            raise ValueError("Cancha, fecha de inicio, franja y solicitante son obligatorios.")
        if not 2 <= self.numero_semanas <= 8:
            raise ValueError("El número de semanas debe estar entre 2 y 8.")
        return ReservaRecurrente(
            self.cancha, self.fecha_inicio, self.franja, self.solicitante,
            self.numero_semanas, self.equipo_prestado, self.notas
        )


# Prototype: deepcopy separa la lista mutable de equipo de cada clon.
class Bloqueo:
    def __init__(self, hora_inicio, hora_fin, equipo_prestado=None, motivo=""):
        self.cancha = None
        self.fecha = None
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.equipo_prestado = list(equipo_prestado or [])
        self.motivo = motivo

    def clonar_para(self, cancha, fecha):
        clon = copy.deepcopy(self)
        clon.cancha = cancha
        clon.fecha = fecha
        return clon
