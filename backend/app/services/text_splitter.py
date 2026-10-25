from typing import List
from app.models.schemas import DocumentChunk
from app.services.document_parser import ParsedDocument

class TextSplitter:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", ". ", "? ", "! ", "; ", " ", ""]

    def _split_text(self, text: str) -> List[str]:
        """
        Recursively splits text into chunks of at most `chunk_size` with `chunk_overlap`.
        """
        if len(text) <= self.chunk_size:
            return [text.strip()] if text.strip() else []

        # Find best separator
        separator = self.separators[-1]
        for sep in self.separators:
            if sep in text:
                separator = sep
                break

        if separator:
            splits = text.split(separator)
        else:
            splits = list(text)

        chunks: List[str] = []
        current_chunk = ""

        for part in splits:
            candidate = f"{current_chunk}{separator}{part}" if current_chunk else part
            if len(candidate) <= self.chunk_size:
                current_chunk = candidate
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                # If a single part is larger than chunk_size, recursively split it
                if len(part) > self.chunk_size:
                    sub_chunks = self._split_text(part)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    # Apply overlap from the tail of current_chunk
                    if self.chunk_overlap > 0 and current_chunk:
                        overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
                        overlap_text = current_chunk[overlap_start:]
                        current_chunk = f"{overlap_text}{separator}{part}".strip()
                    else:
                        current_chunk = part

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def split_document(self, doc: ParsedDocument) -> List[DocumentChunk]:
        """
        Splits each page of the parsed document into chunks while preserving page numbers.
        """
        all_chunks: List[DocumentChunk] = []
        chunk_counter = 0

        for page in doc.pages:
            if not page.text.strip():
                continue

            page_chunks = self._split_text(page.text)
            for chunk_text in page_chunks:
                if not chunk_text.strip():
                    continue

                chunk_counter += 1
                chunk_id = f"{doc.document_id}_p{page.page_number}_c{chunk_counter}"
                all_chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        document_id=doc.document_id,
                        filename=doc.filename,
                        page_number=page.page_number,
                        chunk_index=chunk_counter,
                        text=chunk_text
                    )
                )

        return all_chunks
