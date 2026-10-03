from abc import ABC, abstractmethod

# Strategy
class EstrategiaAtaque(ABC):
    @abstractmethod
    def atacar(self, atacante, enemigo):
        pass


class AtaqueNormal(EstrategiaAtaque):
    def atacar(self, atacante, enemigo):
        dano = atacante.ataque
        enemigo.recibir_dano(dano)
        print(f"{atacante.nombre} usa ataque normal e inflige {dano} de dano.")


class AtaqueFuerte(EstrategiaAtaque):
    def atacar(self, atacante, enemigo):
        dano = atacante.ataque * 2
        enemigo.recibir_dano(dano)
        print(f"{atacante.nombre} usa ataque fuerte e inflige {dano} de dano.")


class Personaje:
    def __init__(self, nombre, vida, ataque):
        self.nombre = nombre
        self.vida = vida
        self.ataque = ataque
        self.estrategia = AtaqueNormal()

    def cambiar_estrategia(self, estrategia):
        self.estrategia = estrategia

    def atacar(self, enemigo):
        self.estrategia.atacar(self, enemigo)

    def recibir_dano(self, dano):
        self.vida = max(0, self.vida - dano)

    def esta_vivo(self):
        return self.vida > 0


class Guerrero(Personaje):
    pass


class Dragon(Personaje):
    pass


class Soldado(Personaje):
    pass


class Alien(Personaje):
    pass


# Factory
class PersonajeFactory:
    @staticmethod
    def crear(tipo):
        if tipo == "guerrero":
            return Guerrero("Guerrero", 100, 20)
        if tipo == "dragon":
            return Dragon("Dragon", 160, 30)
        if tipo == "soldado":
            return Soldado("Soldado", 80, 15)
        if tipo == "alien":
            return Alien("Alien", 120, 25)
        raise ValueError("Tipo de personaje no valido")


# Abstract Factory
class MundoFactoryABC(ABC):
    @abstractmethod
    def crear_jugador(self):
        pass

    @abstractmethod
    def crear_enemigo(self):
        pass


class FantasyFactory(MundoFactoryABC):
    def crear_jugador(self):
        return PersonajeFactory.crear("guerrero")

    def crear_enemigo(self):
        return PersonajeFactory.crear("dragon")


class SciFiFactory(MundoFactoryABC):
    def crear_jugador(self):
        return PersonajeFactory.crear("soldado")

    def crear_enemigo(self):
        return PersonajeFactory.crear("alien")


# Singleton
class GameConfig:
    _objeto = None

    def __init__(self):
        self.dificultad = "normal"
        self.numero_maximo_turnos = 10

    @classmethod
    def obtener_objeto(cls):
        if cls._objeto is None:
            cls._objeto = cls()
        return cls._objeto


# Facade
class GameFacade:
    def __init__(self):
        self.jugador = None
        self.enemigo = None
        self.factory = None
        self.config = GameConfig.obtener_objeto()
        self.turno = 0

    def seleccionar_mundo(self, mundo):
        if mundo == "fantasia":
            self.factory = FantasyFactory()
        elif mundo == "ciencia ficcion":
            self.factory = SciFiFactory()
        else:
            raise ValueError("Mundo no valido. Usa 'fantasia' o 'ciencia ficcion'.")

    def crear_personajes(self):
        if self.factory is None:
            raise ValueError("Primero debes seleccionar un mundo.")
        self.jugador = self.factory.crear_jugador()
        self.enemigo = self.factory.crear_enemigo()

    def seleccionar_estrategia(self, tipo):
        if tipo == "normal":
            self.jugador.cambiar_estrategia(AtaqueNormal())
        elif tipo == "fuerte":
            self.jugador.cambiar_estrategia(AtaqueFuerte())
        else:
            raise ValueError("Estrategia no valida. Usa 'normal' o 'fuerte'.")

    def ejecutar_turno(self, estrategia):
        self.turno += 1
        self.seleccionar_estrategia(estrategia)
        print(f"\n--- Turno {self.turno} ---")

        self.jugador.atacar(self.enemigo)
        print(f"Vida de {self.enemigo.nombre}: {self.enemigo.vida}")

        if self.enemigo.esta_vivo():
            self.enemigo.atacar(self.jugador)
            print(f"Vida de {self.jugador.nombre}: {self.jugador.vida}")

    def determinar_ganador(self):
        if not self.jugador.esta_vivo():
            return f"Gana {self.enemigo.nombre}."
        if not self.enemigo.esta_vivo():
            return f"Gana {self.jugador.nombre}."
        return "No hay ganador: se alcanzo el numero maximo de turnos."

    def jugar(self):
        print(f"Dificultad: {self.config.dificultad}")
        print(f"{self.jugador.nombre} se enfrenta a {self.enemigo.nombre}.")

        while (self.jugador.esta_vivo() and self.enemigo.esta_vivo()
               and self.turno < self.config.numero_maximo_turnos):
            estrategia = self._pedir_estrategia()
            self.ejecutar_turno(estrategia)

        print(f"\n{self.determinar_ganador()}")

    def iniciar(self):
        mundo = self._pedir_mundo()
        self.seleccionar_mundo(mundo)
        self.crear_personajes()
        self.jugar()

    @staticmethod
    def _leer_opcion(mensaje, opciones):
        while True:
            try:
                opcion = input(mensaje).strip().lower()
            except EOFError:
                raise SystemExit(
                    "La partida necesita las elecciones del jugador para iniciar."
                )

            if opcion in opciones:
                return opcion
            print(f"Opcion no valida. Opciones disponibles: {', '.join(opciones)}.")

    def _pedir_mundo(self):
        return self._leer_opcion(
            "Elige mundo [fantasia/ciencia ficcion]: ",
            ("fantasia", "ciencia ficcion"),
        )

    def _pedir_estrategia(self):
        return self._leer_opcion(
            "Elige ataque [normal/fuerte]: ",
            ("normal", "fuerte"),
        )
