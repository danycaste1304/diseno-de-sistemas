
class Inventario:
    def verificar(self, producto):
        print(f"Verificando el stock de {producto}")
        return True

class Pago:
    def procesar(self, monto):
        print(f"Procesando pago: {monto}")
        return True

class Envio:
    def crear_envio(self, producto):
        print(f"Preparando el envio de: {producto}")

class Notificacion:
    def enviar(self, mensaje):
        print(f"Gracias por comprar {mensaje} en TiendaPepitos")

class TiendaFacade:
    def __init__(self):
        self.inventario = Inventario()
        self.pago = Pago()
        self.envio = Envio()
        self.notificacion = Notificacion()

    def comprar(self, producto, precio):
        if not self.inventario.verificar(producto):
            print("No hay stock")
            return

        if not self.pago.procesar(precio):
            print("Fallo el pago")
            return

        self.envio.crear_envio(producto)
        self.notificacion.enviar(producto)

def main():

    tienda=TiendaFacade()
    tienda.comprar("Laptop", 1500)

main()
