import os
import json
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions

from app.config import settings
from app.models.schemas import DocumentChunk, Citation, DocumentInfo

logger = logging.getLogger(__name__)

class VectorStoreService:
    def __init__(self, persist_directory: Optional[str] = None):
        self.persist_directory = persist_directory or settings.CHROMA_PERSIST_DIRECTORY
        os.makedirs(self.persist_directory, exist_ok=True)
        self.registry_file = Path(self.persist_directory) / "documents_registry.json"

        # Initialize ChromaDB persistent client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Initialize Sentence Transformer embedding function
        try:
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=settings.EMBEDDING_MODEL_NAME
            )
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformerEmbeddingFunction ({e}), falling back to DefaultEmbeddingFunction.")
            self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()

        self.collection = self.client.get_or_create_collection(
            name=settings.COLLECTION_NAME,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )
        
        self._load_registry()

    def _load_registry(self) -> Dict[str, Dict[str, Any]]:
        if self.registry_file.exists():
            try:
                with open(self.registry_file, "r", encoding="utf-8") as f:
                    self.registry = json.load(f)
            except Exception as e:
                logger.error(f"Error reading document registry: {e}")
                self.registry = {}
        else:
            self.registry = {}
        return self.registry

    def _save_registry(self):
        try:
            with open(self.registry_file, "w", encoding="utf-8") as f:
                json.dump(self.registry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving document registry: {e}")

    def add_document(self, doc_info: DocumentInfo, chunks: List[DocumentChunk]):
        """
        Store document metadata in registry and chunk embeddings in ChromaDB collection.
        """
        if not chunks:
            # Still record document info even if empty
            self.registry[doc_info.document_id] = doc_info.model_dump()
            self._save_registry()
            return

        ids = [chunk.chunk_id for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        metadatas = [
            {
                "document_id": chunk.document_id,
                "filename": chunk.filename,
                "page_number": int(chunk.page_number),
                "chunk_index": int(chunk.chunk_index),
            }
            for chunk in chunks
        ]

        # Chroma upsert in batches to avoid any single-call payload limits
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            end_idx = i + batch_size
            self.collection.upsert(
                ids=ids[i:end_idx],
                documents=documents[i:end_idx],
                metadatas=metadatas[i:end_idx]
            )

        self.registry[doc_info.document_id] = doc_info.model_dump()
        self._save_registry()

    def delete_document(self, document_id: str) -> bool:
        """
        Delete document from registry and all its vector embeddings from ChromaDB.
        """
        existed = document_id in self.registry
        if existed:
            try:
                self.collection.delete(where={"document_id": document_id})
            except Exception as e:
                logger.error(f"Error deleting embeddings for document {document_id}: {e}")
            del self.registry[document_id]
            self._save_registry()
            return True
        return False

    def get_document_info(self, document_id: str) -> Optional[DocumentInfo]:
        data = self.registry.get(document_id)
        if data:
            return DocumentInfo(**data)
        return None

    def list_documents(self) -> List[DocumentInfo]:
        return [DocumentInfo(**info) for info in self.registry.values()]

    def search_similar_chunks(
        self,
        query: str,
        top_k: int = 4,
        similarity_threshold: float = 0.30,
        document_ids: Optional[List[str]] = None
    ) -> List[Citation]:
        """
        Perform semantic search against indexed chunks and return citations with similarity scores.
        """
        if not query or not str(query).strip():
            return []
        if self.collection.count() == 0:
            return []

        top_k = max(1, min(10, int(top_k)))
        similarity_threshold = max(0.0, min(1.0, float(similarity_threshold)))

        where_clause = None
        if document_ids:
            if len(document_ids) == 1:
                where_clause = {"document_id": document_ids[0]}
            else:
                where_clause = {"document_id": {"$in": document_ids}}

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=min(top_k * 2, max(1, self.collection.count())),
                where=where_clause
            )
        except Exception as e:
            logger.error(f"Query error in ChromaDB: {e}")
            return []

        citations: List[Citation] = []
        if not results or not results["documents"] or not results["documents"][0]:
            return []

        retrieved_texts = results["documents"][0]
        retrieved_metas = results["metadatas"][0] if results.get("metadatas") else []
        retrieved_distances = results["distances"][0] if results.get("distances") else []

        for idx, text in enumerate(retrieved_texts):
            meta = retrieved_metas[idx] if idx < len(retrieved_metas) else {}
            # In cosine space, distance in [0, 2]. Similarity = 1.0 - (distance / 2.0)
            distance = retrieved_distances[idx] if idx < len(retrieved_distances) else 1.0
            similarity = max(0.0, min(1.0, 1.0 - (distance / 2.0)))

            if similarity >= similarity_threshold:
                citations.append(
                    Citation(
                        document_id=meta.get("document_id", "unknown"),
                        filename=meta.get("filename", "unknown"),
                        page_number=int(meta.get("page_number", 1)),
                        excerpt=text,
                        similarity_score=round(similarity, 4)
                    )
                )

        # Sort by similarity score descending and take top_k
        citations.sort(key=lambda c: c.similarity_score, reverse=True)
        return citations[:top_k]

    def total_documents_count(self) -> int:
        return len(self.registry)

    def total_chunks_count(self) -> int:
        try:
            return self.collection.count()
        except Exception:
            return 0

# Global singleton
vector_store = VectorStoreService()
