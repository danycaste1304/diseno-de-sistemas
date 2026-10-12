"""Actualiza flujos modificados del PDF sin alterar las demás páginas.

Las fuentes Mermaid de estos flujos están junto a este script. Se dibujan
en PDF vectorial para conservar texto legible al ampliar la página.
"""

from io import BytesIO
from math import atan2, cos, pi, sin
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas


PDF = Path(__file__).resolve().parents[2] / "DiagramasFlujo_PSet2.pdf"
INK = HexColor("#223649")
LINE = HexColor("#4D6578")
BLUE = HexColor("#EAF3FA")
YELLOW = HexColor("#FFF6DD")
RED = HexColor("#FCECEB")
GREEN = HexColor("#E5F4EA")


def texto(c, contenido, x, y, ancho, tamano=10.5):
    lineas = []
    for parte in contenido.split("\n"):
        lineas.extend(simpleSplit(parte, "Helvetica", tamano, ancho - 20))
    interlineado = tamano + 3
    primer_renglon = y + (len(lineas) - 1) * interlineado / 2 - tamano * 0.34
    c.setFillColor(INK)
    c.setFont("Helvetica", tamano)
    for indice, linea in enumerate(lineas):
        c.drawCentredString(x, primer_renglon - indice * interlineado, linea)


def caja(c, x, y, ancho, alto, contenido, relleno=BLUE, tamano=10.5,
         radio=11):
    c.setFillColor(relleno)
    c.setStrokeColor(INK)
    c.setLineWidth(1.1)
    c.roundRect(x - ancho / 2, y - alto / 2, ancho, alto, radio,
                fill=1, stroke=1)
    texto(c, contenido, x, y, ancho, tamano)


def rombo(c, x, y, ancho, alto, contenido, tamano=10.2):
    c.setFillColor(YELLOW)
    c.setStrokeColor(INK)
    c.setLineWidth(1.1)
    ruta = c.beginPath()
    ruta.moveTo(x, y + alto / 2)
    ruta.lineTo(x + ancho / 2, y)
    ruta.lineTo(x, y - alto / 2)
    ruta.lineTo(x - ancho / 2, y)
    ruta.close()
    c.drawPath(ruta, fill=1, stroke=1)
    texto(c, contenido, x, y, ancho * 0.7, tamano)


def flecha(c, puntos, etiqueta=None, etiqueta_x=None, etiqueta_y=None):
    c.setStrokeColor(LINE)
    c.setFillColor(LINE)
    c.setLineWidth(1.3)
    ruta = c.beginPath()
    ruta.moveTo(*puntos[0])
    for punto in puntos[1:]:
        ruta.lineTo(*punto)
    c.drawPath(ruta)
    x1, y1 = puntos[-2]
    x2, y2 = puntos[-1]
    angulo = atan2(y2 - y1, x2 - x1)
    longitud = 8
    for giro in (pi / 6, -pi / 6):
        c.line(x2, y2,
               x2 - longitud * cos(angulo + giro),
               y2 - longitud * sin(angulo + giro))
    if etiqueta:
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawString(etiqueta_x, etiqueta_y, etiqueta)


def encabezado(c, numero, nombre, requisitos, ancho, alto):
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(ancho / 2, alto - 42, f"{numero}. {nombre}")
    c.setFont("Helvetica", 9.5)
    c.drawCentredString(ancho / 2, alto - 60, requisitos)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.7)
    c.line(48, alto - 72, ancho - 48, alto - 72)


def flujo_reserva():
    ancho, alto = 980, 1350
    memoria = BytesIO()
    c = canvas.Canvas(memoria, pagesize=(ancho, alto))
    encabezado(c, 5, "Reservar una cancha",
               "RF-02, RF-04, RF-05, RF-21, RF-24, RF-27, RNF-05",
               ancho, alto)
    x, xr = 390, 800
    caja(c, x, 1230, 470, 50,
         "Actor: Estudiante; el Capitán participa por herencia")
    caja(c, x, 1160, 470, 56,
         "Precondiciones: autenticado; cancha, fecha y franja seleccionadas",
         BLUE)
    caja(c, x, 1090, 470, 50,
         "1. El solicitante pide reservar cancha, fecha y franja")
    rombo(c, x, 1015, 280, 62,
          "2. ¿Han pasado 15 minutos o menos desde la selección?")
    caja(c, xr, 1015, 270, 60,
         "2a. Cancela el proceso y deja libre la franja. Fin.", RED)
    caja(c, x, 940, 470, 50, "3. El sistema valida suspensión")
    rombo(c, x, 865, 280, 62, "4. ¿El solicitante está suspendido?")
    caja(c, xr, 865, 270, 60,
         "4a. Rechaza e informa la suspensión. Fin.", RED)
    caja(c, x, 790, 470, 50,
         "5. El sistema valida el horario de la sede")
    rombo(c, x, 715, 280, 62, "6. ¿Horario permitido?")
    caja(c, xr, 715, 270, 60,
         "6a. Rechaza e informa el horario permitido. Fin.", RED)
    caja(c, x, 640, 470, 50,
         "7. Aplica la estrategia de prioridad si hay concurrencia")
    rombo(c, x, 565, 280, 62,
          "8. ¿La solicitud conserva la prioridad?")
    caja(c, xr, 565, 270, 60,
         "8a. Rechaza e informa la prioridad. Fin.", RED)
    caja(c, x, 490, 470, 50,
         "9. El creador prepara la reserva con su política de cancelación")
    caja(c, x, 415, 470, 50,
         "10. Verifica disponibilidad y registra de forma atómica")
    rombo(c, x, 340, 280, 62,
          "11. ¿La franja estaba disponible?")
    caja(c, xr, 340, 270, 60,
         "11a. Rechaza sin ocupar la franja. Fin.", RED)
    caja(c, x, 265, 470, 50,
         "12. Notifica por el canal de la sede")
    caja(c, x, 190, 330, 44,
         "Fin: reserva confirmada", GREEN, radio=22)

    eslabones = [
        (1230, 50, 1160, 56, None),
        (1160, 56, 1090, 50, None),
        (1090, 50, 1015, 62, None),
        (1015, 62, 940, 50, "Sí"),
        (940, 50, 865, 62, None),
        (865, 62, 790, 50, "No"),
        (790, 50, 715, 62, None),
        (715, 62, 640, 50, "Sí"),
        (640, 50, 565, 62, None),
        (565, 62, 490, 50, "Sí"),
        (490, 50, 415, 50, None),
        (415, 50, 340, 62, None),
        (340, 62, 265, 50, "Sí"),
        (265, 50, 190, 44, None),
    ]
    for origen, alto_origen, destino, alto_destino, etiqueta in eslabones:
        y1 = origen - alto_origen / 2
        y2 = destino + alto_destino / 2
        flecha(c, [(x, y1), (x, y2)], etiqueta, x + 13, (y1 + y2) / 2)
    for y, etiqueta in [(1015, "No"), (865, "Sí"), (715, "No"),
                        (565, "No"), (340, "No")]:
        flecha(c, [(x + 140, y), (xr - 135, y)], etiqueta,
               x + 190, y + 8)
    c.showPage()
    c.save()
    memoria.seek(0)
    return PdfReader(memoria).pages[0]


def flujo_prioridad():
    ancho, alto = 980, 1200
    memoria = BytesIO()
    c = canvas.Canvas(memoria, pagesize=(ancho, alto))
    encabezado(c, 6, "Reservar con prioridad",
               "RF-04, RF-05, RF-24 y RNF-16", ancho, alto)
    x, xi, xd = 430, 135, 790
    caja(c, x, 1080, 470, 50, "Actor: Capitán")
    caja(c, x, 1010, 510, 56,
         "Precondiciones: autenticado, no suspendido y con solicitudes concurrentes")
    caja(c, x, 940, 470, 50,
         "1. Selecciona cancha, fecha y franja")
    caja(c, x, 870, 470, 50,
         "2. El sistema identifica solicitudes concurrentes")
    rombo(c, x, 790, 320, 70,
          "3. ¿El momento de solicitud es anterior al límite configurado?")
    caja(c, xi, 710, 220, 62,
         "3a. Procesar con prioridad regular", BLUE)
    caja(c, x, 710, 330, 62,
         "4. El sistema verifica prioridad vigente")
    rombo(c, x, 630, 260, 66,
          "5. ¿El capitán tiene prioridad?")
    caja(c, xd, 630, 245, 62,
         "5a. Procesar con prioridad regular", BLUE)
    caja(c, x, 550, 330, 62,
         "6. Seleccionar solicitud prioritaria")
    caja(c, x, 455, 470, 54,
         "7. Validar disponibilidad y confirmar bajo lock")
    rombo(c, x, 365, 270, 66, "8. ¿Puede confirmarse?")
    caja(c, xd, 365, 245, 62,
         "8a. Rechazar e informar motivo. Fin.", RED)
    caja(c, x, 275, 470, 54,
         "9. Confirmar la reserva y notificar resultados", GREEN)
    caja(c, x, 190, 330, 44,
         "Fin: prioridad procesada", GREEN, radio=22)

    for origen, h1, destino, h2, etiqueta in [
        (1080, 50, 1010, 56, None),
        (1010, 56, 940, 50, None),
        (940, 50, 870, 50, None),
        (870, 50, 790, 70, None),
        (790, 70, 710, 62, "Sí"),
        (710, 62, 630, 66, None),
        (630, 66, 550, 62, "Sí"),
        (550, 62, 455, 54, None),
        (455, 54, 365, 66, None),
        (365, 66, 275, 54, "Sí"),
        (275, 54, 190, 44, None),
    ]:
        y1, y2 = origen - h1 / 2, destino + h2 / 2
        flecha(c, [(x, y1), (x, y2)], etiqueta, x + 12, (y1 + y2) / 2)
    flecha(c, [(x - 160, 790), (xi, 790), (xi, 741)], "No", 210, 798)
    flecha(c, [(xi, 679), (xi, 455), (x - 235, 455)])
    flecha(c, [(x + 130, 630), (xd - 122.5, 630)], "No", 590, 640)
    flecha(c, [(xd, 599), (xd, 455), (x + 235, 455)])
    flecha(c, [(x + 135, 365), (xd - 122.5, 365)], "No", 600, 375)
    c.showPage()
    c.save()
    memoria.seek(0)
    return PdfReader(memoria).pages[0]


def flujo_cancelacion():
    ancho, alto = 1100, 1160
    memoria = BytesIO()
    c = canvas.Canvas(memoria, pagesize=(ancho, alto))
    encabezado(c, 7, "Cancelar una reserva",
               "RF-07, RF-08, RF-09, RF-10, RF-11, RF-23, RNF-16",
               ancho, alto)
    x, xi, xd = 550, 255, 760
    caja(c, x, 1040, 480, 50,
         "Actor: Estudiante; el Capitán participa por herencia")
    caja(c, x, 970, 480, 56,
         "Precondiciones: autenticado; reserva propia ACTIVA y no iniciada")
    caja(c, x, 900, 480, 50,
         "1. El solicitante pide cancelar su reserva")
    caja(c, x, 830, 480, 50,
         "2. El sistema verifica propiedad y estado")
    rombo(c, x, 755, 280, 62,
          "3. ¿La reserva puede cancelarse?")
    caja(c, 940, 755, 250, 60,
         "3a. Rechaza e informa el motivo. Fin.", RED)
    caja(c, x, 680, 480, 50,
         "4. La estrategia lee el plazo de 2 h o 24 h de la configuración")
    rombo(c, x, 605, 280, 62,
          "5. ¿Se cumple el plazo antes del inicio?")

    caja(c, xi, 505, 350, 56,
         "6. Pasa a CANCELADA, registra fecha y libera la franja")
    caja(c, xi, 420, 350, 56,
         "7. Registra la cancelación y notifica")
    caja(c, xi, 335, 280, 44,
         "Fin: cancelación regular", GREEN, radio=22)

    caja(c, xd, 505, 350, 56,
         "5a. Pasa a NO_SHOW, registra fecha y libera la franja")
    caja(c, xd, 420, 350, 56,
         "6a. El estudiante registra y cuenta no-shows del mes")
    rombo(c, xd, 335, 270, 65,
          "7a. ¿Alcanzó el límite configurado de 3 no-shows?")
    caja(c, xd, 245, 290, 56,
         "8a. El estudiante crea una suspensión de 7 días")
    caja(c, 1000, 245, 170, 56,
         "8b. Notifica el no-show")
    caja(c, xd, 160, 320, 56,
         "9a. Notifica no-show y suspensión")
    caja(c, xd, 75, 280, 44,
         "Fin: no-show registrado", GREEN, radio=22)

    for origen, alto_origen, destino, alto_destino, etiqueta in [
        (1040, 50, 970, 56, None),
        (970, 56, 900, 50, None),
        (900, 50, 830, 50, None),
        (830, 50, 755, 62, None),
        (755, 62, 680, 50, "Sí"),
        (680, 50, 605, 62, None),
    ]:
        y1, y2 = origen - alto_origen / 2, destino + alto_destino / 2
        flecha(c, [(x, y1), (x, y2)], etiqueta, x + 12, (y1 + y2) / 2)
    flecha(c, [(x + 140, 755), (815, 755)], "No", 710, 763)
    flecha(c, [(x - 140, 605), (xi, 605), (xi, 533)],
           "Sí", 340, 613)
    flecha(c, [(x + 140, 605), (xd, 605), (xd, 533)],
           "No", 702, 613)
    flecha(c, [(xi, 477), (xi, 448)])
    flecha(c, [(xi, 392), (xi, 357)])
    flecha(c, [(xd, 477), (xd, 448)])
    flecha(c, [(xd, 392), (xd, 367.5)])
    flecha(c, [(xd, 302.5), (xd, 273)], "Sí", xd + 12, 286)
    flecha(c, [(xd + 135, 335), (1000, 335), (1000, 273)],
           "No", 910, 345)
    flecha(c, [(xd, 217), (xd, 188)])
    flecha(c, [(xd, 132), (xd, 97)])
    flecha(c, [(1000, 217), (1000, 117), (850, 117), (850, 97)],
           None)
    c.showPage()
    c.save()
    memoria.seek(0)
    return PdfReader(memoria).pages[0]


def flujo_recurrente():
    ancho, alto = 980, 1080
    memoria = BytesIO()
    c = canvas.Canvas(memoria, pagesize=(ancho, alto))
    encabezado(c, 8, "Reservar de forma recurrente",
               "RF-16, RF-17, RF-18, RF-21, RF-27, RNF-09",
               ancho, alto)
    x, xr = 390, 800
    caja(c, x, 970, 470, 50, "Actor: Capitán")
    caja(c, x, 900, 470, 56,
         "Precondiciones: cancha, fecha inicial y franja seleccionadas; semanas opcionales")
    caja(c, x, 830, 470, 50,
         "1. Ingresa datos obligatorios y, si desea, semanas, equipo y notas")
    rombo(c, x, 755, 280, 62, "2. ¿La serie comprende de 2 a 8 semanas?")
    caja(c, xr, 755, 270, 60,
         "2a. Rechaza e informa el rango permitido. Fin.", RED)
    caja(c, x, 680, 470, 50,
         "3. Valida rol, autenticación, suspensión, cancha y sede")
    rombo(c, x, 605, 280, 62,
          "4. ¿Cumple las condiciones iniciales?")
    caja(c, xr, 605, 270, 60,
         "4a. Rechaza sin registrar reservas. Fin.", RED)
    caja(c, x, 530, 470, 50,
         "5. Genera las fechas semanales tentativas")
    caja(c, x, 455, 470, 50,
         "6. Por semana valida horario, disponibilidad y prioridad")
    rombo(c, x, 380, 280, 62,
          "7. ¿Todas las semanas son válidas?")
    caja(c, xr, 380, 270, 64,
         "7a. Informa la primera semana en conflicto y descarta toda la serie. Fin.",
         RED)
    caja(c, x, 305, 470, 50,
         "8. Confirma todas las semanas de forma atómica")
    caja(c, x, 230, 470, 50,
         "9. Guarda equipo y notas, y notifica")
    caja(c, x, 155, 330, 44,
         "Fin: serie confirmada", GREEN, radio=22)

    eslabones = [
        (970, 50, 900, 56, None), (900, 56, 830, 50, None),
        (830, 50, 755, 62, None), (755, 62, 680, 50, "Sí"),
        (680, 50, 605, 62, None), (605, 62, 530, 50, "Sí"),
        (530, 50, 455, 50, None), (455, 50, 380, 62, None),
        (380, 62, 305, 50, "Sí"), (305, 50, 230, 50, None),
        (230, 50, 155, 44, None),
    ]
    for origen, alto_origen, destino, alto_destino, etiqueta in eslabones:
        y1, y2 = origen - alto_origen / 2, destino + alto_destino / 2
        flecha(c, [(x, y1), (x, y2)], etiqueta, x + 13, (y1 + y2) / 2)
    for y in (755, 605, 380):
        flecha(c, [(x + 140, y), (xr - 135, y)],
               "No", x + 190, y + 8)
    c.showPage()
    c.save()
    memoria.seek(0)
    return PdfReader(memoria).pages[0]


def flujo_bloqueo():
    ancho, alto = 1050, 1260
    memoria = BytesIO()
    c = canvas.Canvas(memoria, pagesize=(ancho, alto))
    encabezado(c, 13, "Bloquear canchas para un evento",
               "RF-13, RF-19, RF-20, RF-26",
               ancho, alto)
    x, xi, xd = 500, 280, 800
    caja(c, x, 1145, 520, 50, "Actor: Administrador")
    caja(c, x, 1075, 520, 56,
         "Precondiciones: autenticado; canchas, fechas, franja y motivo identificados")
    caja(c, x, 1005, 520, 50,
         "1. El administrador ingresa los datos del evento")
    caja(c, x, 935, 520, 50,
         "2. El sistema valida sede, fechas y horario")
    rombo(c, x, 860, 280, 62, "3. ¿Los datos son válidos?")
    caja(c, 860, 860, 290, 60,
         "3a. Rechaza e informa los datos inválidos. Fin.", RED)
    caja(c, x, 785, 520, 50,
         "4. Crea una plantilla de bloqueo")
    caja(c, x, 710, 520, 50,
         "5. Clona la plantilla por cancha y fecha")
    caja(c, x, 635, 520, 50,
         "6. Busca reservas activas que coinciden con cada bloqueo")
    rombo(c, x, 560, 280, 62,
          "7. ¿Existen reservas en conflicto?")

    caja(c, xi, 465, 380, 56,
         "7a. Anula cada reserva y registra cada anulación, sin no-show")
    caja(c, xi, 385, 360, 56,
         "8a. Mantiene las franjas BLOQUEADAS")
    caja(c, xi, 305, 360, 56,
         "9a. Registra la creación del bloqueo")
    caja(c, xi, 225, 360, 56,
         "10a. Notifica a los solicitantes afectados")

    caja(c, xd, 465, 300, 56,
         "8. Marca las franjas BLOQUEADAS")
    caja(c, xd, 385, 300, 56,
         "9. Registra la creación del bloqueo")
    caja(c, 540, 145, 320, 44,
         "11. Confirma los bloqueos")
    caja(c, 540, 70, 320, 44,
         "Fin: bloqueos registrados", GREEN, radio=22)

    for origen, alto_origen, destino, alto_destino, etiqueta in [
        (1145, 50, 1075, 56, None), (1075, 56, 1005, 50, None),
        (1005, 50, 935, 50, None), (935, 50, 860, 62, None),
        (860, 62, 785, 50, "Sí"), (785, 50, 710, 50, None),
        (710, 50, 635, 50, None), (635, 50, 560, 62, None),
    ]:
        y1, y2 = origen - alto_origen / 2, destino + alto_destino / 2
        flecha(c, [(x, y1), (x, y2)], etiqueta, x + 12, (y1 + y2) / 2)
    flecha(c, [(640, 860), (715, 860)], "No", 655, 868)
    flecha(c, [(360, 560), (xi, 560), (xi, 493)], "Sí", 295, 568)
    flecha(c, [(640, 560), (xd, 560), (xd, 493)], "No", 700, 568)
    for cx, y1, y2 in ((xi, 437, 413), (xi, 357, 333),
                       (xi, 277, 253), (xd, 437, 413)):
        flecha(c, [(cx, y1), (cx, y2)])
    flecha(c, [(xi, 197), (xi, 183), (500, 183), (500, 167)])
    flecha(c, [(xd, 357), (xd, 183), (580, 183), (580, 167)])
    flecha(c, [(540, 123), (540, 92)])
    c.showPage()
    c.save()
    memoria.seek(0)
    return PdfReader(memoria).pages[0]


def main():
    original = PdfReader(PDF)
    if len(original.pages) != 16:
        raise ValueError("Se esperaban las 16 páginas existentes del PDF de flujos.")
    sustitutas = {
        0: flujo_reserva(),
        1: flujo_prioridad(),
        2: flujo_cancelacion(),
        3: flujo_recurrente(),
        6: flujo_bloqueo(),
    }
    escritor = PdfWriter()
    for indice, pagina in enumerate(original.pages):
        escritor.add_page(sustitutas.get(indice, pagina))
    temporal = PDF.with_suffix(".actualizado.pdf")
    with temporal.open("wb") as archivo:
        escritor.write(archivo)
    temporal.replace(PDF)
    print("Actualizadas las páginas 1, 2, 3, 4 y 7; preservadas las otras 11.")


if __name__ == "__main__":
    main()
