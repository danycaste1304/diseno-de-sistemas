from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.pdfgen import canvas

PDF = Path(__file__).parent / "Diagramas_de_Flujo_PSet2.pdf"
TITULOS = [
    "1. Registrarse",
    "2. Iniciar sesión",
    "3. Consultar disponibilidad",
    "4. Consultar mis reservas",
    "5. Reservar una cancha",
    "6. Reservar con prioridad",
    "7. Cancelar una reserva",
    "8. Reservar de forma recurrente",
    "9. Validar disponibilidad semana por semana",
    "10. Gestionar horarios",
    "11. Asignar prioridad",
    "12. Anular una reserva",
    "13. Bloquear canchas para un evento",
    "14. Anular reservas en conflicto",
    "15. Notificar solicitante afectado",
]

reader = PdfReader(str(PDF))
if len(reader.pages) != len(TITULOS):
    raise ValueError("El número de páginas no coincide con el número de títulos.")

writer = PdfWriter()
for source, title in zip(reader.pages, TITULOS):
    width = float(source.mediabox.width)
    height = float(source.mediabox.height)
    header_height = 38
    buffer = BytesIO()
    page_canvas = canvas.Canvas(buffer, pagesize=(width, height + header_height))
    page_canvas.setFont("Helvetica-Bold", 9)
    page_canvas.drawCentredString(width / 2, height + 22, title)
    page_canvas.setLineWidth(0.5)
    page_canvas.line(18, height + 14, width - 18, height + 14)
    page_canvas.save()
    header_page = PdfReader(buffer).pages[0]
    header_page.merge_transformed_page(source, Transformation().translate(tx=0, ty=0))
    writer.add_page(header_page)

temporary = PDF.with_suffix(".tmp.pdf")
with temporary.open("wb") as stream:
    writer.write(stream)
temporary.replace(PDF)
print(f"Se añadieron títulos a {len(TITULOS)} páginas.")
