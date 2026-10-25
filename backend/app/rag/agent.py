import logging
import re
from typing import List, Optional, Set
from app.config import settings
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    Citation,
)
from app.services.vector_store import vector_store
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

class ResearchAgent:
    """
    Controlled, bounded document research agent for multi-hop retrieval,
    summarization, and cross-document comparison.
    """
    def __init__(self):
        self.vector_store = vector_store
        self.llm_service = llm_service
        self.max_iterations = settings.AGENT_MAX_ITERATIONS

    def _is_conversational_greeting(self, text: str) -> bool:
        cleaned = re.sub(r'[^\w\s]', ' ', text.strip().lower()).strip()
        cleaned = re.sub(r'\s+', ' ', cleaned)
        greetings = {"hi", "hello", "hey", "who are you", "what can you do", "help"}
        if cleaned in greetings:
            return True
        for g in greetings:
            if cleaned.startswith(f"{g} ") or cleaned.endswith(f" {g}"):
                return True
        return False

    def _detect_comparison_or_multi_topic(self, text: str) -> Optional[List[str]]:
        """
        Check if query asks for a comparison or multiple concepts, e.g.:
        "compare A and B", "difference between X and Y"
        """
        lower = text.lower()
        compare_match = re.search(r'(?:compare|differences? between|contrast)\s+(.+?)\s+(?:and|with|to|vs\.?)\s+(.+)', lower)
        if compare_match:
            topic_a = compare_match.group(1).strip()
            topic_b = compare_match.group(2).strip().rstrip('?')
            return [topic_a, topic_b]
        return None

    def run(self, request: ChatRequest) -> ChatResponse:
        steps: List[str] = []
        user_query = request.message.strip()
        
        # Step 1: Check if query is simple greeting or requires document retrieval
        if self._is_conversational_greeting(user_query):
            steps.append("Analyzed intent: Conversational greeting detected (no document retrieval needed).")
            return ChatResponse(
                answer=(
                    "Hello! I am your AI Document Research Assistant. "
                    "You can upload PDF, DOCX, or TXT documents using the panel on the left, "
                    "and I will help you analyze, search, summarize, and cross-reference them with source citations."
                ),
                citations=[],
                mode="agent",
                retrieved_chunks_count=0,
                agent_steps=steps,
                suggested_followups=[
                    "What documents are currently loaded?",
                    "Can you summarize the uploaded documents?",
                    "Compare key findings across the documents."
                ]
            )

        steps.append(f"Analyzed query: '{user_query}' - Document retrieval is required.")
        
        all_citations: List[Citation] = []
        seen_excerpts: Set[str] = set()

        def add_unique_citations(retrieved: List[Citation]):
            for cit in retrieved:
                norm = cit.excerpt.strip()[:100]
                if norm not in seen_excerpts:
                    seen_excerpts.add(norm)
                    all_citations.append(cit)

        # Step 2: Primary retrieval
        steps.append(f"Iteration 1: Executing primary semantic retrieval (top_k={request.top_k}).")
        initial_results = self.vector_store.search_similar_chunks(
            query=user_query,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            document_ids=request.document_ids
        )
        add_unique_citations(initial_results)
        steps.append(f"Iteration 1 found {len(initial_results)} matching chunks.")

        # Step 3: Check if cross-document comparison or sub-query expansion is needed
        sub_topics = self._detect_comparison_or_multi_topic(user_query)
        if sub_topics and len(sub_topics) >= 2:
            steps.append(f"Detected comparative analysis between: '{sub_topics[0]}' and '{sub_topics[1]}'.")
            for idx, topic in enumerate(sub_topics[:2], start=2):
                if idx > self.max_iterations:
                    break
                steps.append(f"Iteration {idx}: Targeted sub-query retrieval for topic '{topic}'.")
                sub_results = self.vector_store.search_similar_chunks(
                    query=topic,
                    top_k=2,
                    similarity_threshold=request.similarity_threshold,
                    document_ids=request.document_ids
                )
                add_unique_citations(sub_results)
                steps.append(f"Retrieved {len(sub_results)} additional relevant chunks for '{topic}'.")
        elif len(all_citations) < 2 and self.max_iterations >= 2:
            # Multi-hop fallback: expand query with synonyms or key terms
            steps.append("Iteration 2: Initial retrieval yielded limited evidence. Performing broadened query search.")
            broadened_query = f"{user_query} overview key concepts details"
            broad_results = self.vector_store.search_similar_chunks(
                query=broadened_query,
                top_k=request.top_k,
                similarity_threshold=max(0.15, request.similarity_threshold - 0.10),
                document_ids=request.document_ids
            )
            add_unique_citations(broad_results)
            steps.append(f"Broadened search added {len(broad_results)} candidate chunks.")

        # Step 4: Verification and synthesis
        if not all_citations:
            steps.append("Search concluded: No relevant document evidence found.")
            return ChatResponse(
                answer="The uploaded documents do not contain sufficient information to answer this question.",
                citations=[],
                mode="agent",
                retrieved_chunks_count=0,
                agent_steps=steps,
                suggested_followups=[
                    "What documents are currently loaded?",
                    "Can you summarize the uploaded files?"
                ]
            )

        # Sort combined citations by relevance score
        all_citations.sort(key=lambda c: c.similarity_score, reverse=True)
        final_citations = all_citations[:request.top_k * 2]

        steps.append(f"Synthesizing final answer grounded in {len(final_citations)} verified excerpts across documents.")
        answer_text, followups = self.llm_service.generate_answer(
            query=user_query,
            citations=final_citations,
            history=request.conversation_history
        )

        return ChatResponse(
            answer=answer_text,
            citations=final_citations,
            mode="agent",
            retrieved_chunks_count=len(final_citations),
            agent_steps=steps,
            suggested_followups=followups
        )

# Global agent instance
research_agent = ResearchAgent()
