import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from google.adk.tools import FunctionTool


def generate_pdf(title: str, content_blocks: list[str]) -> bytes:
    """Generates a formatted PDF document from a title and content blocks.

    Args:
        title: The title of the PDF document.
        content_blocks: A list of text blocks to include in the document.

    Returns:
        The generated PDF as bytes.
    """
    buffer = io.BytesIO()
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = [Paragraph(title, styles["Title"]), Spacer(1, 12)]
    for block in content_blocks:
        for line in block.split("\n"):
            if line.strip():
                story.append(Paragraph(line, styles["Normal"]))
                story.append(Spacer(1, 6))
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


pdf_export_tool = FunctionTool(func=generate_pdf)
