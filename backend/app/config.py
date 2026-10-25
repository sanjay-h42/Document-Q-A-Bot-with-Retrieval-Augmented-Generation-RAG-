import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings(BaseSettings):
    APP_NAME: str = "Document Q&A RAG API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3-flash-preview"
    
    # Vector Database & Embeddings
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    CHROMA_PERSIST_DIRECTORY: str = str(BASE_DIR / "chroma_db")
    COLLECTION_NAME: str = "rag_documents"
    
    # RAG Chunking & Retrieval Parameters
    DEFAULT_CHUNK_SIZE: int = 800
    DEFAULT_CHUNK_OVERLAP: int = 150
    DEFAULT_TOP_K: int = 4
    SIMILARITY_THRESHOLD: float = 0.30  # Minimum relevance score (0.0 to 1.0)
    
    # Security & File Limits
    MAX_FILE_SIZE_MB: int = 25
    ALLOWED_EXTENSIONS: set[str] = {".pdf", ".docx", ".txt"}
    ALLOWED_MIME_TYPES: set[str] = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "application/octet-stream",  # Fallback for some browsers on txt/docx
    }
    
    # Agent Parameters
    AGENT_MAX_ITERATIONS: int = 3
    
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
