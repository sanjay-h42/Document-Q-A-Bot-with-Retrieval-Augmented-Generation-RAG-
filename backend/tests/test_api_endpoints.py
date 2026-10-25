import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.vector_store import vector_store

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "vector_store_status" in data
    assert "gemini_configured" in data

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"

def test_upload_invalid_file_extension():
    response = client.post(
        "/api/documents/upload",
        files=[("files", ("malicious.exe", b"not a valid document", "application/octet-stream"))]
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]

def test_upload_empty_file():
    response = client.post(
        "/api/documents/upload",
        files=[("files", ("empty.txt", b"", "text/plain"))]
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"]

def test_document_lifecycle_and_chat():
    sample_text = (
        "Kubernetes is an open-source container orchestration system for automating "
        "software deployment, scaling, and management. It was originally designed by Google."
    ).encode('utf-8')

    # 1. Upload
    upload_res = client.post(
        "/api/documents/upload",
        files=[("files", ("k8s_overview.txt", sample_text, "text/plain"))]
    )
    assert upload_res.status_code == 201
    upload_data = upload_res.json()
    assert len(upload_data) == 1
    doc_id = upload_data[0]["document_id"]
    assert upload_data[0]["filename"] == "k8s_overview.txt"

    # 2. List documents
    list_res = client.get("/api/documents")
    assert list_res.status_code == 200
    docs = list_res.json()
    assert any(d["document_id"] == doc_id for d in docs)

    # 3. Chat with uploaded document
    chat_payload = {
        "message": "Who originally designed Kubernetes?",
        "top_k": 2,
        "similarity_threshold": 0.20,
        "mode": "standard"
    }
    chat_res = client.post("/api/chat", json=chat_payload)
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    assert chat_data["retrieved_chunks_count"] > 0
    assert "Google" in chat_data["citations"][0]["excerpt"]

    # 4. Clear chat
    clear_res = client.post("/api/chat/clear")
    assert clear_res.status_code == 200

    # 5. Delete document
    del_res = client.delete(f"/api/documents/{doc_id}")
    assert del_res.status_code == 200

    # 6. Verify deleted
    list_after = client.get("/api/documents").json()
    assert not any(d["document_id"] == doc_id for d in list_after)
