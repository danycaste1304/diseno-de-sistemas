#Vehiculo -> mueva -> mover()

#Auto -> mueve por carretera
#Bote -> mueve por agua
#Avion -> mueve por aire

class Mover:
    def mover(self):
        raise NotImplementedError

class MoverCarretera(Mover):
    def mover(self):
        print("Conduciendo por carretera")

class MoverAgua(Mover):
    def mover(self):
        print("Navegando por")

class MoverAire(Mover):
    def mover(self):
        print("Volando por aire")

class Vehiculo:
    def __init__(self, comportamiento_mover):
        self.comportamiento_mover = comportamiento_mover

    def mover(self):
        self.comportamiento_mover.mover()


class Auto(Vehiculo):
    def __init__(self):
        super().__init__(MoverCarretera())

class Bote(Vehiculo):
    def __init__(self):
        super().__init__(MoverAgua())

class Avion(Vehiculo):
    def __init__(self):
        super().__init__(MoverAire())

if __name__ == "__main__":
    auto = Auto()
    auto.mover()

    print()

    bote = Bote()
    bote.mover()

    print()

    avion = Avion()
    avion.mover()