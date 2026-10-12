"""Genera el diagrama de actividad vectorial de la reserva recurrente.

La secuencia reproduce el flujo 08: el Builder valida sus datos, se verifican
las condiciones iniciales y luego se examina cada semana antes de confirmar
toda la serie en una única operación.
"""

from pathlib import Path
import sys

from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

from redibujar_casos_secuencia import BLUE, GREEN, INK, LINE, RED, YELLOW, texto


def caja(c, x, y, ancho, alto, contenido, color=BLUE, tamano=11):
    c.setFillColor(color)
    c.setStrokeColor(INK)
    c.setLineWidth(1.4)
    c.roundRect(x - ancho / 2, y - alto / 2, ancho, alto, 11,
                fill=1, stroke=1)
    texto(c, contenido, x, y, ancho - 20, tamano)


def decision(c, x, y, ancho, alto, contenido):
    c.setFillColor(YELLOW)
    c.setStrokeColor(INK)
    c.setLineWidth(1.4)
    trazo = c.beginPath()
    trazo.moveTo(x, y + alto / 2)
    trazo.lineTo(x + ancho / 2, y)
    trazo.lineTo(x, y - alto / 2)
    trazo.lineTo(x - ancho / 2, y)
    trazo.close()
    c.drawPath(trazo, fill=1, stroke=1)
    texto(c, contenido, x, y, ancho * .70, 10.7)


def flecha(c, puntos, etiqueta=None, lugar=None):
    c.setStrokeColor(LINE)
    c.setLineWidth(1.6)
    trazo = c.beginPath()
    trazo.moveTo(*puntos[0])
    for punto in puntos[1:]:
        trazo.lineTo(*punto)
    c.drawPath(trazo)
    x1, y1 = puntos[-2]
    x2, y2 = puntos[-1]
    c.setFillColor(LINE)
    trazo = c.beginPath()
    if abs(x2 - x1) >= abs(y2 - y1):
        signo = 1 if x2 > x1 else -1
        trazo.moveTo(x2, y2)
        trazo.lineTo(x2 - signo * 10, y2 + 5)
        trazo.lineTo(x2 - signo * 10, y2 - 5)
    else:
        signo = 1 if y2 > y1 else -1
        trazo.moveTo(x2, y2)
        trazo.lineTo(x2 + 5, y2 - signo * 10)
        trazo.lineTo(x2 - 5, y2 - signo * 10)
    trazo.close()
    c.drawPath(trazo, fill=1, stroke=0)
    if etiqueta and lugar:
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(*lugar, etiqueta)


def inicio(c, x, y):
    c.setFillColor(INK)
    c.circle(x, y, 13, fill=1, stroke=0)


def fin(c, x, y):
    c.setFillColor(HexColor("#FFFFFF"))
    c.setStrokeColor(INK)
    c.setLineWidth(1.5)
    c.circle(x, y, 14, fill=1, stroke=1)
    c.setFillColor(INK)
    c.circle(x, y, 9, fill=1, stroke=0)


def generar(destino):
    ancho, alto = 1250, 1680
    c = canvas.Canvas(str(destino), pagesize=(ancho, alto))
    c.setTitle("ReservaU - Actividad de reserva recurrente")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(ancho / 2, 1647,
                        "ReservaU - Actividad de reserva recurrente")
    c.setFont("Helvetica", 10.5)
    c.drawCentredString(ancho / 2, 1626,
                        "Validación previa, revisión semanal y confirmación atómica de la serie")

    # Carriles de responsabilidad.
    c.setStrokeColor(LINE)
    c.setLineWidth(1.2)
    c.rect(30, 80, 1190, 1515, fill=0, stroke=1)
    c.line(300, 80, 300, 1595)
    c.line(30, 1552, 1220, 1552)
    c.setFillColor(BLUE)
    c.rect(31, 1553, 268, 41, fill=1, stroke=0)
    c.rect(301, 1553, 918, 41, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(165, 1568, "Capitán")
    c.drawCentredString(760, 1568, "Sistema")

    inicio(c, 165, 1495)
    caja(c, 165, 1385, 230, 110,
         "Ingresa cancha, fecha inicial, franja y solicitante; "
         "semanas, equipo y notas opcionales", BLUE, 10.7)
    caja(c, 550, 1385, 280, 76,
         "Builder: valida los datos obligatorios y el número de semanas", BLUE, 10.8)
    decision(c, 550, 1280, 230, 98, "¿Serie de 2 a 8 semanas?")
    caja(c, 945, 1280, 255, 70,
         "Informar rango válido; ninguna reserva registrada", RED, 10.5)
    fin(c, 945, 1200)

    caja(c, 550, 1155, 300, 78,
         "Validar rol de capitán, sesión, suspensión, cancha y sede", BLUE, 10.8)
    decision(c, 550, 1040, 230, 98, "¿Cumple condiciones iniciales?")
    caja(c, 945, 1040, 255, 70,
         "Informar rechazo; ninguna reserva registrada", RED, 10.5)
    fin(c, 945, 960)

    caja(c, 550, 920, 275, 75,
         "Generar fechas semanales y lista temporal vacía", BLUE, 10.8)
    decision(c, 550, 805, 220, 98, "¿Quedan semanas por revisar?")
    caja(c, 850, 735, 245, 72,
         "Identificar la fecha y franja de la semana actual", BLUE, 10.6)
    caja(c, 850, 635, 245, 88,
         "Validar horario de sede, disponibilidad y prioridad", BLUE, 10.6)
    decision(c, 850, 520, 220, 98, "¿Semana válida?")
    caja(c, 850, 420, 245, 72,
         "Agregar a la lista temporal; avanzar a la semana siguiente", BLUE, 10.6)
    caja(c, 1080, 520, 205, 95,
         "Descartar la lista; informar la primera semana en conflicto", RED, 10.2)
    fin(c, 1080, 435)

    caja(c, 550, 415, 285, 82,
         "Confirmar toda la serie en una única operación", GREEN, 11)
    caja(c, 550, 290, 285, 92,
         "Guardar equipo y notas; notificar por la sede correspondiente", GREEN, 10.8)
    caja(c, 165, 290, 230, 74,
         "Recibe confirmación de la serie", GREEN, 10.7)
    fin(c, 165, 180)

    flecha(c, [(165, 1482), (165, 1440)])
    flecha(c, [(280, 1385), (410, 1385)])
    flecha(c, [(550, 1347), (550, 1329)])
    flecha(c, [(665, 1280), (817, 1280)], "No", (720, 1291))
    flecha(c, [(945, 1245), (945, 1214)])
    flecha(c, [(550, 1231), (550, 1194)], "Sí", (562, 1212))
    flecha(c, [(550, 1116), (550, 1089)])
    flecha(c, [(665, 1040), (817, 1040)], "No", (720, 1051))
    flecha(c, [(945, 1005), (945, 974)])
    flecha(c, [(550, 991), (550, 958)], "Sí", (562, 978))
    flecha(c, [(550, 882), (550, 854)])
    flecha(c, [(660, 805), (735, 805), (735, 785), (850, 785),
               (850, 771)], "Sí", (682, 818))
    flecha(c, [(850, 699), (850, 679)])
    flecha(c, [(850, 591), (850, 569)])
    flecha(c, [(850, 471), (850, 456)], "Sí", (862, 462))
    flecha(c, [(960, 520), (977, 520)], "No", (965, 535))
    flecha(c, [(1080, 472), (1080, 449)])
    # El recorrido de vuelta utiliza el borde del carril Sistema.
    flecha(c, [(850, 384), (850, 355), (1190, 355), (1190, 880),
               (550, 880), (550, 854)])
    flecha(c, [(550, 756), (550, 456)], "No", (562, 735))
    flecha(c, [(550, 374), (550, 336)])
    flecha(c, [(407, 290), (280, 290)])
    flecha(c, [(165, 253), (165, 194)])

    c.setFillColor(INK)
    c.setFont("Helvetica", 10)
    c.drawCentredString(625, 125,
                        "Un conflicto descarta todas las semanas tentativas; ninguna reserva parcial queda confirmada.")
    c.showPage()
    c.save()


if __name__ == "__main__":
    raiz = Path(__file__).resolve().parents[1]
    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else raiz / "Actividad_Pset2.pdf"
    generar(destino)
    print(f"Creado {destino}")
