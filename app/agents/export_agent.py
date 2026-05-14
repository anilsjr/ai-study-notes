import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class PDFExportAgent:
    def __init__(self):
        self.styles = getSampleStyleSheet()

    def generate_pdf(self, title: str, content_blocks: list[str]) -> bytes:
        """
        Generates a beautifully formatted PDF given structured content blocks.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []

        title_style = self.styles['Title']
        normal_style = self.styles['Normal']

        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 12))

        for block in content_blocks:
            # simple text split for demonstration
            for paragraph_text in block.split('\n'):
                if paragraph_text.strip():
                    story.append(Paragraph(paragraph_text, normal_style))
                    story.append(Spacer(1, 6))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
