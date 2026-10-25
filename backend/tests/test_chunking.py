import pytest
from app.services.text_splitter import TextSplitter
from app.services.document_parser import ParsedDocument, DocumentPage

def test_chunking_metadata_preservation():
    splitter = TextSplitter(chunk_size=100, chunk_overlap=20)
    pages = [
        DocumentPage(page_number=1, text="Page 1 sentence one. Page 1 sentence two. " * 3),
        DocumentPage(page_number=2, text="Page 2 data point. Page 2 data point two. " * 3)
    ]
    parsed_doc = ParsedDocument(
        document_id="doc_test_123",
        filename="test.pdf",
        file_type="pdf",
        total_pages=2,
        pages=pages
    )
    
    chunks = splitter.split_document(parsed_doc)
    assert len(chunks) > 0
    
    # Check that metadata is preserved on all chunks
    for chunk in chunks:
        assert chunk.document_id == "doc_test_123"
        assert chunk.filename == "test.pdf"
        assert chunk.page_number in [1, 2]
        assert chunk.chunk_id.startswith("doc_test_123_p")
        assert len(chunk.text) > 0

def test_chunking_short_document():
    splitter = TextSplitter(chunk_size=500, chunk_overlap=50)
    pages = [
        DocumentPage(page_number=1, text="Brief short sentence.")
    ]
    parsed_doc = ParsedDocument(
        document_id="short_doc",
        filename="short.txt",
        file_type="txt",
        total_pages=1,
        pages=pages
    )
    chunks = splitter.split_document(parsed_doc)
    assert len(chunks) == 1
    assert chunks[0].text == "Brief short sentence."
    assert chunks[0].page_number == 1
