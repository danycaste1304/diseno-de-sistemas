class ReglaPrioridad:
    def tiene_prioridad(self, hora):
        raise NotImplementedError


class PrioridadAntes18(ReglaPrioridad):
    def tiene_prioridad(self, hora):
        return hora.hour < 18


class SinPrioridad(ReglaPrioridad):
    def tiene_prioridad(self, hora):
        return False
