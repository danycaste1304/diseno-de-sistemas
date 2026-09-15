from singleton import GestorDeConfiguracion, reserva_permitida

def test_rechaza_reserva():
    config = GestorDeConfiguracion.obtener_objeto()
    config.modo_mantenimiento = True

    assert reserva_permitida(config) is False

# En un inicio no funciona porque se queda con le valor establecido en la anterior prueba, ya que es como una variable global
def test_reserva_aceptada():
    config = GestorDeConfiguracion.obtener_objeto()
    config.modo_mantenimiento = False

    assert reserva_permitida(config) is True