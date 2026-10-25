import type {
  DocumentInfo,
  DocumentUploadResponse,
  ChatRequest,
  ChatResponse,
  HealthStatus,
  SuggestedQuestionsResponse,
} from '../types';

const API_BASE = '/api';

export async function fetchHealth(): Promise<HealthStatus> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
  return res.json();
}

export async function fetchDocuments(): Promise<DocumentInfo[]> {
  const res = await fetch(`${API_BASE}/documents`);
  if (!res.ok) throw new Error(`Failed to fetch documents: ${res.statusText}`);
  return res.json();
}

export async function uploadDocuments(files: File[]): Promise<DocumentUploadResponse[]> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });

  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorData.detail || 'Failed to upload documents');
  }

  return res.json();
}

export async function deleteDocument(documentId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/documents/${documentId}`, {
    method: 'DELETE',
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorData.detail || 'Failed to delete document');
  }
}

export async function fetchSuggestedQuestions(documentId: string): Promise<SuggestedQuestionsResponse> {
  const res = await fetch(`${API_BASE}/documents/${documentId}/suggested-questions`);
  if (!res.ok) throw new Error(`Failed to fetch suggested questions: ${res.statusText}`);
  return res.json();
}

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorData.detail || 'Error communicating with RAG assistant');
  }

  return res.json();
}

export async function clearChat(): Promise<void> {
  await fetch(`${API_BASE}/chat/clear`, {
    method: 'POST',
  });
}
