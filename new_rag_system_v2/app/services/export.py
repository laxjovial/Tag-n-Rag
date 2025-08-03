import io
from docx import Document as DocxDocument
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph

class ExportService:
    """
    A service to export text content to various file formats.
    """
    def to_txt(self, content: str) -> io.BytesIO:
        """Exports content to a TXT file in memory."""
        buffer = io.BytesIO()
        buffer.write(content.encode('utf-8'))
        buffer.seek(0)
        return buffer

    def to_docx(self, content: str) -> io.BytesIO:
        """Exports content to a DOCX file in memory."""
        document = DocxDocument()
        document.add_paragraph(content)
        buffer = io.BytesIO()
        document.save(buffer)
        buffer.seek(0)
        return buffer

    def to_pdf(self, content: str) -> io.BytesIO:
        """Exports content to a PDF file in memory."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [Paragraph(line, styles['Normal']) for line in content.split('\n')]
        doc.build(story)
        buffer.seek(0)
        return buffer
