# app/services/pdf_generator.py

from weasyprint import HTML, CSS
from io import BytesIO
from jinja2 import Environment, FileSystemLoader, select_autoescape
import logging

logger = logging.getLogger(__name__)

class PDFGenerator:
    def __init__(self):
        # Jinja2 setup
        self.env = Environment(
            loader=FileSystemLoader("app/templates"),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    async def generar_pdf_factura(
        self,
        factura,
        cliente,
        items,
        empresa
    ) -> BytesIO:
        """
        Genera PDF de factura usando Weasyprint + HTML/CSS.
        """
        try:
            # 1. Renderizar template
            template = self.env.get_template("facturas/factura.html")
            html_string = template.render(
                factura=factura,
                cliente=cliente,
                items=items,
                empresa=empresa
            )
            
            # 2. Generar PDF
            buffer = BytesIO()
            HTML(string=html_string).write_pdf(buffer)
            buffer.seek(0)
            
            logger.info(f"PDF factura {factura.numero_comprobante} generado exitosamente")
            
            return buffer
        
        except Exception as e:
            logger.error(f"Error generando PDF: {e}", exc_info=True)
            raise
    
    async def generar_pdf_cotizacion(
        self,
        cotizacion,
        cliente,
        items,
        empresa,
        vendedor=None,
        cuentas_bancarias=None,
    ) -> BytesIO:
        """Genera PDF de cotización."""
        template = self.env.get_template("cotizaciones/cotizacion.html")
        html_string = template.render(
            cotizacion=cotizacion,
            cliente=cliente,
            items=items,
            empresa=empresa,
            vendedor=vendedor,
            cuentas_bancarias=cuentas_bancarias or [],
        )
        
        buffer = BytesIO()
        HTML(string=html_string).write_pdf(buffer)
        buffer.seek(0)
        
        return buffer


# Instancia global
pdf_generator = PDFGenerator()