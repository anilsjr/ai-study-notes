import io
import PyPDF2
from docx import Document

class DocumentParser:
    @staticmethod
    def parse_pdf(file_bytes: bytes) -> str:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
        return text

    @staticmethod
    def parse_docx(file_bytes: bytes) -> str:
        doc = Document(io.BytesIO(file_bytes))
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> list[str]:
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - overlap
        return chunks
