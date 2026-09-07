class Cancha:
    def __init__(self, nombre, tipo, habilitada=True):
        self.nombre = nombre
        self.tipo = tipo
        self.habilitada = habilitada
        self.disponibilidades = []

    def esta_habilitada(self):
        return self.habilitada

    def agregar_disponibilidad(self, disponibilidad):
        self.disponibilidades.append(disponibilidad)
