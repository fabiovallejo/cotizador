from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

def generar_pdf_cotizacion(cotizacion):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    y = height - 50

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, "COTIZACIÓN")
    y -= 30

    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, y, f"Código: {cotizacion.codigo_cotizacion}")
    y -= 15
    pdf.drawString(50, y, f"Estado: {cotizacion.estado}")
    y -= 15
    pdf.drawString(50, y, f"Cliente ID: {cotizacion.id_cliente}")
    y -= 25

    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, y, "Producto")
    pdf.drawString(250, y, "Cantidad")
    pdf.drawString(320, y, "Precio")
    pdf.drawString(400, y, "Subtotal")
    y -= 15

    pdf.setFont("Helvetica", 10)

    for item in cotizacion.items:
        pdf.drawString(50, y, item.nombre_producto)
        pdf.drawString(260, y, str(item.cantidad))
        pdf.drawString(330, y, f"{float(item.precio_unitario):.2f}")
        pdf.drawString(410, y, f"{float(item.subtotal):.2f}")
        y -= 15

        if y < 50:
            pdf.showPage()
            y = height - 50

    y -= 20
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(330, y, "TOTAL:")
    pdf.drawString(410, y, f"{float(cotizacion.total):.2f}")

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return buffer
