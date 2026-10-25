import pytest
import shutil
import tempfile
from pathlib import Path
from app.services.vector_store import VectorStoreService
from app.models.schemas import DocumentInfo, DocumentChunk

@pytest.fixture
def temp_vector_store():
    temp_dir = tempfile.mkdtemp()
    store = VectorStoreService(persist_directory=temp_dir)
    yield store
    shutil.rmtree(temp_dir, ignore_errors=True)

def test_add_and_search_document(temp_vector_store):
    doc_info = DocumentInfo(
        document_id="doc_vec_1",
        filename="ai_guide.txt",
        file_type="txt",
        file_size_bytes=500,
        total_pages=1,
        chunk_count=2,
        uploaded_at="2026-10-22T00:00:00Z"
    )
    
    chunks = [
        DocumentChunk(
            chunk_id="chunk_1",
            document_id="doc_vec_1",
            filename="ai_guide.txt",
            page_number=1,
            chunk_index=1,
            text="Transformer models utilize self-attention mechanisms to process sequence data efficiently."
        ),
        DocumentChunk(
            chunk_id="chunk_2",
            document_id="doc_vec_1",
            filename="ai_guide.txt",
            page_number=1,
            chunk_index=2,
            text="Convolutional neural networks are tailored for spatial 2D grid data like computer vision images."
        )
    ]
    
    temp_vector_store.add_document(doc_info, chunks)
    assert temp_vector_store.total_documents_count() == 1
    assert temp_vector_store.total_chunks_count() == 2
    
    # Query for transformers
    results = temp_vector_store.search_similar_chunks(
        query="How do transformers process sequence data?",
        top_k=2,
        similarity_threshold=0.20
    )
    assert len(results) > 0
    assert results[0].filename == "ai_guide.txt"
    assert "self-attention" in results[0].excerpt
    assert results[0].similarity_score > 0.20

def test_delete_document(temp_vector_store):
    doc_info = DocumentInfo(
        document_id="doc_to_delete",
        filename="remove_me.txt",
        file_type="txt",
        file_size_bytes=100,
        total_pages=1,
        chunk_count=1,
        uploaded_at="2026-10-22T00:00:00Z"
    )
    chunks = [
        DocumentChunk(
            chunk_id="del_chunk_1",
            document_id="doc_to_delete",
            filename="remove_me.txt",
            page_number=1,
            chunk_index=1,
            text="This chunk should be removed completely."
        )
    ]
    temp_vector_store.add_document(doc_info, chunks)
    assert temp_vector_store.total_documents_count() == 1
    
    deleted = temp_vector_store.delete_document("doc_to_delete")
    assert deleted is True
    assert temp_vector_store.total_documents_count() == 0
    assert temp_vector_store.total_chunks_count() == 0
    
    # Deleting non-existent returns False
    assert temp_vector_store.delete_document("non_existent") is False
