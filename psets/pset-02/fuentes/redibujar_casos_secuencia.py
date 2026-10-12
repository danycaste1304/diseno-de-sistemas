"""Genera en PDF vectorial los casos de uso y la secuencia de reserva.

Los PDF anteriores eran imágenes JPEG de una página y no tenían fuente
editable en el repositorio. Este archivo permite ajustar ambos diagramas.
"""

from pathlib import Path
import sys

from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas


INK = HexColor("#223649")
LINE = HexColor("#52677A")
ASSOCIATION = HexColor("#8A9BA8")
BLUE = HexColor("#EAF3FA")
YELLOW = HexColor("#FFF6DD")
GREEN = HexColor("#E5F4EA")
RED = HexColor("#FCECEB")


def texto(c, contenido, x, y, ancho, tamano=10.5, fuente="Helvetica"):
    lineas = []
    for parte in contenido.split("\n"):
        lineas.extend(simpleSplit(parte, fuente, tamano, ancho))
    paso = tamano + 3
    primera = y + (len(lineas) - 1) * paso / 2 - tamano * 0.34
    c.setFillColor(INK)
    c.setFont(fuente, tamano)
    for indice, linea in enumerate(lineas):
        c.drawCentredString(x, primera - indice * paso, linea)


def punta(c, x, y, direccion, abierta=False):
    c.setStrokeColor(LINE)
    c.setFillColor(HexColor("#FFFFFF") if abierta else LINE)
    if direccion == "izquierda":
        vertices = [(x, y), (x + 9, y + 5), (x + 9, y - 5)]
    else:
        vertices = [(x, y), (x - 9, y + 5), (x - 9, y - 5)]
    trazado = c.beginPath()
    trazado.moveTo(*vertices[0])
    for vertice in vertices[1:]:
        trazado.lineTo(*vertice)
    trazado.close()
    c.drawPath(trazado, fill=1, stroke=1)


def actor(c, x, y, nombre):
    c.setStrokeColor(INK)
    c.setLineWidth(1.4)
    c.circle(x, y + 21, 10, fill=0, stroke=1)
    c.line(x, y + 11, x, y - 21)
    c.line(x - 20, y, x + 20, y)
    c.line(x, y - 21, x - 18, y - 43)
    c.line(x, y - 21, x + 18, y - 43)
    texto(c, nombre, x, y - 62, 150, 10.5, "Helvetica-Bold")


def caso(c, x, y, titulo):
    c.setFillColor(BLUE)
    c.setStrokeColor(INK)
    c.setLineWidth(1.2)
    c.ellipse(x - 145, y - 26, x + 145, y + 26, fill=1, stroke=1)
    texto(c, titulo, x, y, 235, 10.4)


def relacion(c, origen_y, destino_y, etiqueta, columna):
    """Traza una relación UML desde el caso base al caso incluido o extendido."""
    derecha = 735
    c.setStrokeColor(LINE)
    c.setLineWidth(1.1)
    c.setDash(5, 3)
    ruta = c.beginPath()
    ruta.moveTo(derecha, origen_y)
    ruta.lineTo(columna, origen_y)
    ruta.lineTo(columna, destino_y)
    ruta.lineTo(derecha, destino_y)
    c.drawPath(ruta)
    c.setDash()
    punta(c, derecha, destino_y, "izquierda", abierta=True)
    c.setFillColor(INK)
    c.setFont("Helvetica", 9.5)
    centro = (origen_y + destino_y) / 2
    c.drawString(columna + 7, centro, etiqueta)


def bloque_precondiciones(c, x, ancho, titulo, entradas):
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, 475, titulo)
    y = 445
    for entrada in entradas:
        lineas = simpleSplit(entrada, "Helvetica", 9.7, ancho)
        c.setFont("Helvetica", 9.7)
        for linea in lineas:
            c.drawString(x, y, linea)
            y -= 14
        y -= 10


def generar_casos_uso(destino):
    ancho, alto = 1000, 1600
    c = canvas.Canvas(str(destino), pagesize=(ancho, alto))
    c.setTitle("ReservaU - Diagrama de casos de uso")
    c.translate(0, -250)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 19)
    c.drawCentredString(ancho / 2, 1812, "ReservaU - Casos de uso")
    c.setFont("Helvetica", 10)
    c.drawCentredString(ancho / 2, 1790,
                        "Las flechas <<include>> apuntan al caso incluido y las <<extend>> al caso base")
    c.setStrokeColor(INK)
    c.setLineWidth(1.1)
    c.rect(350, 565, 550, 1180, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(365, 1718, "Sistema ReservaU")

    casos = [
        (1660, "Registrarse"),
        (1590, "Iniciar sesión"),
        (1520, "Consultar disponibilidad"),
        (1450, "Consultar mis reservas"),
        (1380, "Reservar una cancha"),
        (1310, "Cancelar una reserva"),
        (1230, "Reservar con prioridad"),
        (1160, "Reservar de forma recurrente"),
        (1090, "Validar disponibilidad semana por semana"),
        (990, "Gestionar horarios"),
        (920, "Asignar prioridad"),
        (850, "Bloquear canchas para un evento"),
        (780, "Anular reservas en conflicto"),
        (710, "Anular una reserva"),
        (640, "Notificar solicitante afectado"),
    ]

    c.setStrokeColor(ASSOCIATION)
    c.setLineWidth(0.8)
    for origen, destinos in [
        (1490, [1660, 1590, 1520, 1450, 1380, 1310]),
        (1190, [1230, 1160]),
        (850, [990, 920, 850, 710]),
    ]:
        for destino_y in destinos:
            c.line(145, origen, 445, destino_y)

    relacion(c, 1230, 1380, "<<extend>>", 790)
    relacion(c, 1160, 1090, "<<include>>", 810)
    relacion(c, 780, 850, "<<extend>>", 830)
    relacion(c, 780, 640, "<<include>>", 870)
    relacion(c, 710, 640, "<<include>>", 840)

    for y, nombre in casos:
        caso(c, 590, y, nombre)
    actor(c, 110, 1490, "Estudiante")
    actor(c, 110, 1190, "Capitán")
    actor(c, 110, 850, "Administrador")
    c.setDash(5, 3)
    c.setStrokeColor(LINE)
    c.line(55, 1190, 55, 1490)
    c.line(55, 1190, 85, 1190)
    c.line(55, 1490, 85, 1490)
    c.setDash()
    punta(c, 85, 1490, "derecha", abierta=True)
    c.setFillColor(INK)
    c.setFont("Helvetica", 9.5)
    c.drawString(15, 1340, "es un")

    c.setStrokeColor(LINE)
    c.line(42, 525, 958, 525)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(45, 495, "Precondiciones principales")
    bloque_precondiciones(c, 45, 270, "Estudiante", [
        "Registrarse: correo y contraseña; cuenta inexistente.",
        "Iniciar sesión: cuenta registrada.",
        "Consultar: usuario autenticado.",
        "Reservar: autenticado, no suspendido; cancha, fecha y franja.",
        "Cancelar: reserva propia activa y aún no iniciada.",
    ])
    bloque_precondiciones(c, 350, 270, "Capitán", [
        "Prioridad: solicitudes concurrentes antes del límite configurado.",
        "Recurrente: autenticado y no suspendido; cancha, fecha y franja.",
        "Semanas: entre 2 y 8; si se omite, se usan 2.",
    ])
    bloque_precondiciones(c, 655, 300, "Administrador", [
        "Funciones administrativas: sesión iniciada y rol de administrador.",
        "Horarios: cancha identificada.",
        "Prioridad: estudiante registrado identificado.",
        "Bloqueo: canchas, fechas, franja y motivo.",
        "Anulación: reserva activa y motivo identificado.",
    ])
    c.showPage()
    c.save()


def mensaje(c, x1, x2, y, contenido, respuesta=False):
    c.setStrokeColor(LINE)
    c.setLineWidth(1.1)
    c.setDash(4, 3) if respuesta else c.setDash()
    c.line(x1, y, x2, y)
    c.setDash()
    punta(c, x2, y, "derecha" if x2 > x1 else "izquierda",
          abierta=respuesta)
    texto(c, contenido, (x1 + x2) / 2, y + 13,
          abs(x2 - x1) - 10, 9.2)


def generar_secuencia(destino):
    ancho, alto = 1600, 1120
    c = canvas.Canvas(str(destino), pagesize=(ancho, alto))
    c.setTitle("ReservaU - Diagrama de secuencia de reserva")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 19)
    c.drawCentredString(ancho / 2, 1080,
                        "ReservaU - Secuencia de una reserva")
    c.setFont("Helvetica", 10)
    c.drawCentredString(ancho / 2, 1058,
                        "RF-02, RF-04, RF-05, RF-21, RF-22, RF-24, RF-27 y RNF-05")

    posiciones = [85, 260, 435, 610, 785, 960, 1135, 1310, 1485]
    nombres = [
        "Estudiante / Capitán", "Pantalla de reserva", "ReservaFacade",
        "Estudiante", "Validador de sede", "Strategy de prioridad",
        "Disponibilidad", "FabricaReservas", "Notificador de sede",
    ]
    c.setStrokeColor(LINE)
    c.setLineWidth(1)
    c.setDash(5, 4)
    for x in posiciones:
        c.line(x, 976, x, 145)
    c.setDash()
    c.setFillColor(HexColor("#FFFFFF"))
    c.rect(45, 160, 1510, 810, fill=0, stroke=1)
    c.setFillColor(BLUE)
    c.roundRect(48, 948, 164, 21, 4, fill=1, stroke=1)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(57, 955, "alt [solicitud válida]")
    c.line(45, 300, 1555, 300)
    c.setFillColor(RED)
    c.roundRect(48, 278, 390, 21, 4, fill=1, stroke=1)
    c.setFillColor(INK)
    c.drawString(57, 285,
                 "else [tiempo agotado o alguna validación falla]")

    for x, nombre in zip(posiciones, nombres):
        c.setFillColor(BLUE)
        c.setStrokeColor(INK)
        c.roundRect(x - 70, 978, 140, 56, 7, fill=1, stroke=1)
        texto(c, nombre, x, 1006, 126, 9.3, "Helvetica-Bold")

    actor_x, pantalla, fachada, estudiante, sede, prioridad, disponibilidad, creador, notificador = posiciones
    mensaje(c, actor_x, pantalla, 925, "1. Solicitar reserva")
    mensaje(c, pantalla, fachada, 882, "2. reservar(...)")
    c.setFillColor(YELLOW)
    c.setStrokeColor(INK)
    c.roundRect(fachada - 90, 818, 180, 43, 5, fill=1, stroke=1)
    texto(c, "3. Validar sesión y plazo de 15 min", fachada, 839, 170, 9)
    mensaje(c, fachada, estudiante, 790,
            "4. esta_suspendido(momento)")
    mensaje(c, fachada, sede, 745,
            "5. validador.validar(inicio, fin)")
    mensaje(c, fachada, prioridad, 700,
            "6. Si compiten: tiene_prioridad(momento)")
    mensaje(c, fachada, creador, 655,
            "7. elegir_creador() y crear_reserva(...)")
    mensaje(c, creador, fachada, 610,
            "8. Reserva con estrategia de cancelación", respuesta=True)
    mensaje(c, fachada, disponibilidad, 565,
            "9. confirmar_si_disponible() bajo lock")
    mensaje(c, disponibilidad, fachada, 520,
            "10. Confirmada", respuesta=True)
    mensaje(c, fachada, notificador, 475,
            "11. notificar por canal de la sede")
    mensaje(c, notificador, fachada, 430,
            "12. Envío registrado", respuesta=True)
    mensaje(c, fachada, pantalla, 385,
            "13. Reserva confirmada", respuesta=True)
    mensaje(c, pantalla, actor_x, 340,
            "14. Mostrar confirmación", respuesta=True)

    mensaje(c, fachada, pantalla, 245,
            "15. Rechazo sin registrar", respuesta=True)
    mensaje(c, pantalla, actor_x, 200,
            "16. Mostrar motivo", respuesta=True)
    c.setFillColor(INK)
    c.setFont("Helvetica", 10)
    c.drawCentredString(ancho / 2, 102,
                        "La confirmación de disponibilidad y reserva ocurre en una sola sección crítica.")
    c.drawCentredString(ancho / 2, 84,
                        "Una solicitud fallida deja la franja disponible; la notificación ocurre después de confirmar.")
    c.showPage()
    c.save()


if __name__ == "__main__":
    raiz = Path(__file__).resolve().parents[1]
    salida_casos = Path(sys.argv[1]) if len(sys.argv) > 1 else raiz / "CasosUso_Pset2.pdf"
    salida_secuencia = Path(sys.argv[2]) if len(sys.argv) > 2 else raiz / "Secuencia_Pset2.pdf"
    generar_casos_uso(salida_casos)
    generar_secuencia(salida_secuencia)
    print(f"Creados {salida_casos} y {salida_secuencia}")
