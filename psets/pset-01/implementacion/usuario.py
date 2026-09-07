class Usuario:
    def __init__(self, nombre, email, contrasena):
        self.nombre = nombre
        self.email = email
        self.contrasena = contrasena
        self.registrado = False

    def registrarse(self):
        self.registrado = True
        return f"{self.nombre} se registró correctamente."

    def iniciar_sesion(self, contrasena):
        return self.registrado and self.contrasena == contrasena
