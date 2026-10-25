export interface Citation {
  document_id: string;
  filename: string;
  page_number: number;
  excerpt: string;
  similarity_score: number;
}

export interface DocumentInfo {
  document_id: string;
  filename: string;
  file_type: string;
  file_size_bytes: number;
  total_pages: number;
  chunk_count: number;
  uploaded_at: string;
}

export interface DocumentUploadResponse {
  document_id: string;
  filename: string;
  file_type: string;
  total_pages: number;
  chunks_created: number;
  message: string;
  suggested_questions: string[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  citations?: Citation[];
  timestamp: string;
  mode?: 'standard' | 'agent';
  agent_steps?: string[];
}

export interface ChatRequest {
  message: string;
  conversation_history?: {
    role: 'user' | 'assistant' | 'system';
    content: string;
  }[];
  document_ids?: string[];
  top_k?: number;
  similarity_threshold?: number;
  mode?: 'standard' | 'agent';
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  mode: 'standard' | 'agent';
  retrieved_chunks_count: number;
  suggested_followups: string[];
  agent_steps?: string[];
}

export interface HealthStatus {
  status: string;
  app_version: string;
  gemini_configured: boolean;
  vector_store_status: string;
  total_documents: number;
  total_chunks: number;
}

export interface SuggestedQuestionsResponse {
  document_id: string;
  filename: string;
  questions: string[];
}
