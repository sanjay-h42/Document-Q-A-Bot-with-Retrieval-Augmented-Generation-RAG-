import pytest
import shutil
import tempfile
from app.rag.agent import ResearchAgent
from app.models.schemas import ChatRequest
from app.services.vector_store import VectorStoreService

@pytest.fixture
def isolated_agent():
    temp_dir = tempfile.mkdtemp()
    store = VectorStoreService(persist_directory=temp_dir)
    agent = ResearchAgent()
    agent.vector_store = store
    
    # Ingest two distinct topics for comparison testing
    doc1 = (
        "REST APIs use standard HTTP verbs such as GET, POST, PUT, DELETE.\n"
        "They rely on stateless communication and represent state using JSON or XML."
    ).encode('utf-8')
    doc2 = (
        "GraphQL is a query language for APIs developed by Facebook.\n"
        "It allows clients to request exactly the data they need, preventing over-fetching."
    ).encode('utf-8')
    
    from app.services.document_parser import DocumentParser
    from app.services.text_splitter import TextSplitter
    from app.models.schemas import DocumentInfo
    
    p1 = DocumentParser.parse(doc1, "doc_rest", "rest_api.txt", ".txt")
    p2 = DocumentParser.parse(doc2, "doc_graphql", "graphql_api.txt", ".txt")
    
    splitter = TextSplitter(chunk_size=500, chunk_overlap=50)
    c1 = splitter.split_document(p1)
    c2 = splitter.split_document(p2)
    
    store.add_document(
        DocumentInfo(document_id="doc_rest", filename="rest_api.txt", file_type="txt", file_size_bytes=len(doc1), total_pages=1, chunk_count=len(c1), uploaded_at="2026-10-22T00:00:00Z"),
        c1
    )
    store.add_document(
        DocumentInfo(document_id="doc_graphql", filename="graphql_api.txt", file_type="txt", file_size_bytes=len(doc2), total_pages=1, chunk_count=len(c2), uploaded_at="2026-10-22T00:00:00Z"),
        c2
    )
    
    yield agent
    shutil.rmtree(temp_dir, ignore_errors=True)

def test_agent_conversational_greeting(isolated_agent):
    req = ChatRequest(message="Hello! What can you do?", mode="agent")
    res = isolated_agent.run(req)
    assert res.mode == "agent"
    assert res.retrieved_chunks_count == 0
    assert "AI Document Research Assistant" in res.answer
    assert res.agent_steps is not None
    assert any("greeting detected" in s for s in res.agent_steps)

def test_agent_multi_document_comparison(isolated_agent):
    req = ChatRequest(
        message="Compare REST and GraphQL APIs in terms of data fetching",
        mode="agent",
        similarity_threshold=0.15
    )
    res = isolated_agent.run(req)
    assert res.mode == "agent"
    assert res.agent_steps is not None
    assert any("Detected comparative analysis" in s for s in res.agent_steps)
    assert len(res.citations) > 0
    # Check that it retrieved evidence
    filenames = {c.filename for c in res.citations}
    assert "rest_api.txt" in filenames or "graphql_api.txt" in filenames
