import pytest
import shutil
import tempfile
from unittest.mock import MagicMock
from app.rag.pipeline import RAGPipeline
from app.models.schemas import ChatRequest, Citation
from app.services.vector_store import VectorStoreService

@pytest.fixture
def isolated_pipeline():
    temp_dir = tempfile.mkdtemp()
    store = VectorStoreService(persist_directory=temp_dir)
    pipeline = RAGPipeline()
    pipeline.vector_store = store
    
    # Ingest a sample document
    txt_content = (
        "Project Apollo was the third United States human spaceflight program carried out by NASA.\n"
        "It succeeded in landing the first humans on the Moon in July 1969 with Neil Armstrong and Buzz Aldrin.\n"
        "The Saturn V rocket was used as the primary launch vehicle for the Apollo lunar missions."
    ).encode('utf-8')
    
    pipeline.ingest_document(txt_content, "apollo_history.txt", ".txt")
    
    yield pipeline
    shutil.rmtree(temp_dir, ignore_errors=True)

def test_rag_pipeline_answer_supported_query(isolated_pipeline):
    req = ChatRequest(
        message="What rocket was used for the Apollo lunar missions?",
        top_k=2,
        similarity_threshold=0.20,
        mode="standard"
    )
    res = isolated_pipeline.answer_question(req)
    assert res.retrieved_chunks_count > 0
    assert len(res.citations) > 0
    assert res.citations[0].filename == "apollo_history.txt"
    assert "Saturn V" in res.citations[0].excerpt
    assert len(res.answer) > 0

def test_rag_pipeline_unsupported_query(isolated_pipeline):
    req = ChatRequest(
        message="What is the recipe for baking chocolate chip cookies?",
        top_k=2,
        similarity_threshold=0.85,  # High threshold ensures no match
        mode="standard"
    )
    res = isolated_pipeline.answer_question(req)
    assert res.retrieved_chunks_count == 0
    assert len(res.citations) == 0
    assert "The uploaded documents do not contain sufficient information to answer this question" in res.answer
