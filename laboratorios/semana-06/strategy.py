from abc import ABC, abstractmethod

class EstrategiaDescuento(ABC):
    @abstractmethod
    def aplicar(self, precio_base):
        pass

class SinDescuento(EstrategiaDescuento):
    def aplicar(self, precio_base):
        return precio_base

class DescuentoVip(EstrategiaDescuento):
    def aplicar(self, precio_base):
        return precio_base * 0.80  

class DescuentoEstudiante(EstrategiaDescuento):
    def aplicar(self, precio_base):
        return precio_base * 0.95

class DescuentoEmpleado(EstrategiaDescuento):
    def aplicar(self, precio_base):
        return precio_base * 0.75

class Compra:
    def __init__(self, estrategiaDescuento):
        self.estrategiaDescuento = estrategiaDescuento

    def calcular_total(self, precio):
        return self.estrategiaDescuento.aplicar(precio)

def main():

    sin_descuento = SinDescuento()
    descuento_vip = DescuentoVip()
    estud_descuento = DescuentoEstudiante()
    empleado_descuento = DescuentoEmpleado()

    compra_1=Compra(sin_descuento)
    print(compra_1.calcular_total(100))  

    compra_2=Compra(descuento_vip)
    print(compra_2.calcular_total(1000))

    compra_3=Compra(estud_descuento)
    print(compra_3.calcular_total(10))

    compra_4=Compra(empleado_descuento)
    print(compra_4.calcular_total(100))

main()