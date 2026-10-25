import logging
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query

from app.config import settings
from app.core.security import sanitize_filename, validate_file_metadata, validate_file_content
from app.models.schemas import (
    DocumentUploadResponse,
    DocumentInfo,
    ChatRequest,
    ChatResponse,
    ClearChatResponse,
    HealthResponse,
    SuggestedQuestionsResponse,
)
from app.services.vector_store import vector_store
from app.services.llm_service import llm_service
from app.rag.pipeline import rag_pipeline
from app.rag.agent import research_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Document Q&A RAG"])

@router.post(
    "/documents/upload",
    response_model=List[DocumentUploadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload multiple PDF, DOCX, or TXT documents"
)
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Accepts one or more documents (.pdf, .docx, .txt), validates, chunks,
    generates embeddings, stores in ChromaDB, and returns processing status.
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided for upload."
        )

    responses: List[DocumentUploadResponse] = []
    
    for file in files:
        ext = validate_file_metadata(file)
        cleaned_filename = sanitize_filename(file.filename)
        
        try:
            content = await file.read()
            validate_file_content(content, ext)
            
            # Ingest through RAG pipeline
            res = rag_pipeline.ingest_document(
                content=content,
                filename=cleaned_filename,
                ext=ext
            )
            responses.append(res)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to ingest document '{file.filename}': {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing '{file.filename}': {str(e)}"
            )

    return responses

@router.get(
    "/documents",
    response_model=List[DocumentInfo],
    summary="List all indexed documents"
)
async def list_documents():
    """
    Returns list of all documents currently indexed in the vector store with metadata.
    """
    return vector_store.list_documents()

@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a document and its embeddings"
)
async def delete_document(document_id: str):
    """
    Deletes the document from the registry and removes all associated vector chunks from ChromaDB.
    """
    deleted = vector_store.delete_document(document_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found."
        )
    return {"status": "success", "message": f"Document {document_id} and all related chunks were successfully removed."}

@router.get(
    "/documents/{document_id}/suggested-questions",
    response_model=SuggestedQuestionsResponse,
    summary="Get recommended questions for an uploaded document"
)
async def get_suggested_questions(document_id: str):
    doc_info = vector_store.get_document_info(document_id)
    if not doc_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found."
        )
        
    # Retrieve top 2 sample chunks to form questions
    sample_chunks = vector_store.search_similar_chunks(
        query="main overview introduction summary",
        top_k=2,
        similarity_threshold=0.0,
        document_ids=[document_id]
    )
    
    sample_text = " ".join([c.excerpt for c in sample_chunks])
    questions = llm_service.generate_suggested_questions(sample_text, doc_info.filename)
    
    return SuggestedQuestionsResponse(
        document_id=document_id,
        filename=doc_info.filename,
        questions=questions
    )

@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Ask a question about uploaded documents"
)
async def chat(request: ChatRequest):
    """
    Processes user query using either Standard RAG (retrieval + prompt + LLM)
    or Controlled Research Agent (multi-hop retrieval, cross-doc comparison, reasoning).
    """
    # Check if any documents are uploaded
    if vector_store.total_documents_count() == 0:
        return ChatResponse(
            answer="No documents have been uploaded yet. Please upload a PDF, DOCX, or TXT document using the left sidebar to start asking questions.",
            citations=[],
            mode=request.mode,
            retrieved_chunks_count=0,
            suggested_followups=[]
        )

    try:
        if request.mode == "agent":
            return research_agent.run(request)
        else:
            return rag_pipeline.answer_question(request)
    except Exception as e:
        logger.error(f"Error handling chat request: {e}", exc_info=True)
        return ChatResponse(
            answer=f"I encountered a temporary issue while answering: {str(e)}. Please try rephrasing your question.",
            citations=[],
            mode=request.mode,
            retrieved_chunks_count=0,
            suggested_followups=[
                "What documents are currently indexed?",
                "Can you summarize the uploaded files?"
            ]
        )

@router.post(
    "/chat/clear",
    response_model=ClearChatResponse,
    summary="Clear conversation session"
)
async def clear_chat():
    """
    Acknowledges clearing chat history.
    """
    return ClearChatResponse(
        status="success",
        message="Chat session cleared successfully."
    )

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System and dependencies health check"
)
async def health_check():
    """
    Checks health of the API, ChromaDB vector store, and Gemini API configuration.
    """
    return HealthResponse(
        status="healthy",
        app_version=settings.APP_VERSION,
        gemini_configured=llm_service.is_configured(),
        vector_store_status="connected",
        total_documents=vector_store.total_documents_count(),
        total_chunks=vector_store.total_chunks_count()
    )
