import uuid
import datetime
import logging
from typing import List, Optional
from app.config import settings
from app.models.schemas import (
    DocumentUploadResponse,
    DocumentInfo,
    ChatRequest,
    ChatResponse,
    Citation,
)
from app.services.document_parser import DocumentParser
from app.services.text_splitter import TextSplitter
from app.services.vector_store import vector_store
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self):
        self.vector_store = vector_store
        self.llm_service = llm_service
        self.text_splitter = TextSplitter(
            chunk_size=settings.DEFAULT_CHUNK_SIZE,
            chunk_overlap=settings.DEFAULT_CHUNK_OVERLAP
        )

    def ingest_document(self, content: bytes, filename: str, ext: str) -> DocumentUploadResponse:
        """
        Full ingestion pipeline: parse -> chunk -> embed -> store -> generate questions.
        """
        document_id = str(uuid.uuid4())
        
        # 1. Parse document
        parsed_doc = DocumentParser.parse(content, document_id, filename, ext)
        
        # 2. Chunk text preserving page metadata
        chunks = self.text_splitter.split_document(parsed_doc)
        
        # 3. Create document record
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        doc_info = DocumentInfo(
            document_id=document_id,
            filename=filename,
            file_type=ext.lstrip('.'),
            file_size_bytes=len(content),
            total_pages=parsed_doc.total_pages,
            chunk_count=len(chunks),
            uploaded_at=now_str
        )
        
        # 4. Store in vector database
        self.vector_store.add_document(doc_info, chunks)
        
        # 5. Generate suggested questions based on initial content
        sample_text = ""
        for page in parsed_doc.pages:
            if page.text:
                sample_text += page.text + "\n"
            if len(sample_text) > 1000:
                break
                
        suggested = self.llm_service.generate_suggested_questions(sample_text, filename)
        
        return DocumentUploadResponse(
            document_id=document_id,
            filename=filename,
            file_type=ext.lstrip('.'),
            total_pages=parsed_doc.total_pages,
            chunks_created=len(chunks),
            message="Document successfully processed and indexed into vector database.",
            suggested_questions=suggested
        )

    def answer_question(self, request: ChatRequest) -> ChatResponse:
        """
        Retrieval, context formulation, and answer generation.
        """
        # 1. Retrieve relevant chunks
        citations = self.vector_store.search_similar_chunks(
            query=request.message,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            document_ids=request.document_ids
        )
        
        # 2. If no chunks found, return strict negative response
        if not citations:
            return ChatResponse(
                answer="The uploaded documents do not contain sufficient information to answer this question.",
                citations=[],
                mode="standard",
                retrieved_chunks_count=0,
                suggested_followups=[
                    "What documents are currently uploaded?",
                    "Can you summarize what topics are available?"
                ]
            )
            
        # 3. Generate answer grounded in citations
        answer_text, followups = self.llm_service.generate_answer(
            query=request.message,
            citations=citations,
            history=request.conversation_history
        )
        
        return ChatResponse(
            answer=answer_text,
            citations=citations,
            mode="standard",
            retrieved_chunks_count=len(citations),
            suggested_followups=followups
        )

# Global pipeline instance
rag_pipeline = RAGPipeline()
