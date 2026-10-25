import io
import re
from typing import List
from pydantic import BaseModel
try:
    import pymupdf as fitz
except ImportError:
    import fitz  # PyMuPDF

from docx import Document as DocxDocument

class DocumentPage(BaseModel):
    page_number: int
    text: str

class ParsedDocument(BaseModel):
    document_id: str
    filename: str
    file_type: str
    total_pages: int
    pages: List[DocumentPage]

class DocumentParser:
    @staticmethod
    def parse_pdf(content: bytes, document_id: str, filename: str) -> ParsedDocument:
        """
        Extract text page-by-page from PDF using PyMuPDF (fitz).
        """
        doc = fitz.open(stream=content, filetype="pdf")
        pages: List[DocumentPage] = []
        
        try:
            total_pages = len(doc)
            for page_idx in range(total_pages):
                page = doc.load_page(page_idx)
                raw_text = page.get_text("text")
                # Normalize line breaks and spaces
                cleaned = re.sub(r'[ \t]+', ' ', raw_text).strip()
                if cleaned:
                    pages.append(DocumentPage(page_number=page_idx + 1, text=cleaned))
                else:
                    # Keep record of empty page for accurate page indexing
                    pages.append(DocumentPage(page_number=page_idx + 1, text=""))
            
            return ParsedDocument(
                document_id=document_id,
                filename=filename,
                file_type="pdf",
                total_pages=total_pages,
                pages=pages
            )
        finally:
            doc.close()

    @staticmethod
    def parse_docx(content: bytes, document_id: str, filename: str) -> ParsedDocument:
        """
        Extract text from DOCX using python-docx, detecting page breaks or section breaks.
        """
        docx_file = io.BytesIO(content)
        doc = DocxDocument(docx_file)
        
        pages: List[DocumentPage] = []
        current_page_num = 1
        current_page_text: List[str] = []
        
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            # Check for page break in runs
            has_break = False
            for run in paragraph.runs:
                if 'w:br' in run._r.xml and 'w:type="page"' in run._r.xml:
                    has_break = True
                    break
            
            if text:
                current_page_text.append(text)
                
            if has_break:
                full_page_text = "\n\n".join(current_page_text).strip()
                pages.append(DocumentPage(page_number=current_page_num, text=full_page_text))
                current_page_num += 1
                current_page_text = []

        # Also extract table text
        for table in doc.tables:
            table_lines = []
            for row in table.rows:
                row_cells = [cell.text.strip() for cell in row.cells]
                table_lines.append(" | ".join(row_cells))
            if table_lines:
                current_page_text.append("\n".join(table_lines))

        if current_page_text or not pages:
            full_page_text = "\n\n".join(current_page_text).strip()
            pages.append(DocumentPage(page_number=current_page_num, text=full_page_text))

        return ParsedDocument(
            document_id=document_id,
            filename=filename,
            file_type="docx",
            total_pages=len(pages),
            pages=pages
        )

    @staticmethod
    def parse_txt(content: bytes, document_id: str, filename: str) -> ParsedDocument:
        """
        Extract text from TXT, supporting UTF-8 and Latin-1 encoding, splitting by form feed if present.
        """
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            text = content.decode('latin-1', errors='replace')
        
        # Check for form feed character '\x0c' (traditional page break in text files)
        raw_pages = text.split('\x0c')
        pages: List[DocumentPage] = []
        
        for idx, page_str in enumerate(raw_pages):
            cleaned = page_str.strip()
            if cleaned or len(raw_pages) == 1:
                pages.append(DocumentPage(page_number=idx + 1, text=cleaned))
                
        if not pages:
            pages.append(DocumentPage(page_number=1, text=""))

        return ParsedDocument(
            document_id=document_id,
            filename=filename,
            file_type="txt",
            total_pages=len(pages),
            pages=pages
        )

    @classmethod
    def parse(cls, content: bytes, document_id: str, filename: str, ext: str) -> ParsedDocument:
        ext = ext.lower()
        if ext == ".pdf":
            return cls.parse_pdf(content, document_id, filename)
        elif ext == ".docx":
            return cls.parse_docx(content, document_id, filename)
        elif ext == ".txt":
            return cls.parse_txt(content, document_id, filename)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
