from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    page_number: int
    chunk_index: int
    text: str

class Citation(BaseModel):
    document_id: str
    filename: str
    page_number: int
    excerpt: str
    similarity_score: float = 0.0

class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    file_type: str
    file_size_bytes: int
    total_pages: int
    chunk_count: int
    uploaded_at: str

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    file_type: str
    total_pages: int
    chunks_created: int
    message: str
    suggested_questions: List[str] = Field(default_factory=list)

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    citations: Optional[List[Citation]] = None
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_history: List[ChatMessage] = Field(default_factory=list)
    document_ids: Optional[List[str]] = None
    top_k: int = Field(default=4, ge=1, le=10)
    similarity_threshold: float = Field(default=0.30, ge=0.0, le=1.0)
    mode: Literal["standard", "agent"] = "standard"

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    mode: Literal["standard", "agent"] = "standard"
    retrieved_chunks_count: int = 0
    suggested_followups: List[str] = Field(default_factory=list)
    agent_steps: Optional[List[str]] = None

class ClearChatResponse(BaseModel):
    status: str
    message: str

class HealthResponse(BaseModel):
    status: str
    app_version: str
    gemini_configured: bool
    vector_store_status: str
    total_documents: int
    total_chunks: int

class SuggestedQuestionsResponse(BaseModel):
    document_id: str
    filename: str
    questions: List[str]
