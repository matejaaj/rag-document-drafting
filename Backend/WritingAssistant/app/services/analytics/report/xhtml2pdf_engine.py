from __future__ import annotations
from io import BytesIO

from xhtml2pdf import pisa

from app.services.analytics.report.report_models import PdfEngine


class Xhtml2PdfEngine(PdfEngine):
    def html_to_pdf(self, html: str) -> bytes:
        pdf_buffer = BytesIO()
        result = pisa.CreatePDF(src=html, dest=pdf_buffer, encoding="utf-8")
        if result.err:
            raise RuntimeError("xhtml2pdf failed to generate the PDF.")
        return pdf_buffer.getvalue()
