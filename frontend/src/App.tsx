import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { ChatWindow } from './components/ChatWindow';
import { SettingsModal } from './components/SettingsModal';
import {
  fetchDocuments,
  uploadDocuments,
  deleteDocument,
  sendChatMessage,
  clearChat,
  fetchHealth,
} from './services/api';
import type { DocumentInfo, ChatMessage, HealthStatus } from './types';

export const App: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);
  const [health, setHealth] = useState<HealthStatus | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState<boolean>(false);

  // Settings
  const [topK, setTopK] = useState<number>(4);
  const [similarityThreshold, setSimilarityThreshold] = useState<number>(0.30);
  const [mode, setMode] = useState<'standard' | 'agent'>('standard');

  useEffect(() => {
    loadHealthAndDocs();
  }, []);

  const loadHealthAndDocs = async () => {
    try {
      const [h, docs] = await Promise.all([fetchHealth(), fetchDocuments()]);
      setHealth(h);
      setDocuments(docs);
    } catch (err) {
      console.error('Initialization error:', err);
    }
  };

  const handleUpload = async (files: File[]) => {
    setIsUploading(true);
    try {
      const results = await uploadDocuments(files);
      const updatedDocs = await fetchDocuments();
      setDocuments(updatedDocs);
      const updatedHealth = await fetchHealth();
      setHealth(updatedHealth);

      // Extract new suggested questions from uploaded docs
      const newQuestions: string[] = [];
      results.forEach((r) => {
        if (r.suggested_questions && r.suggested_questions.length > 0) {
          newQuestions.push(...r.suggested_questions);
        }
      });

      if (newQuestions.length > 0) {
        setSuggestedQuestions(newQuestions.slice(0, 4));
      }
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteDocument = async (id: string) => {
    await deleteDocument(id);
    setSelectedDocIds((prev) => prev.filter((d) => d !== id));
    const updatedDocs = await fetchDocuments();
    setDocuments(updatedDocs);
    const updatedHealth = await fetchHealth();
    setHealth(updatedHealth);
  };

  const handleToggleDocSelection = (id: string) => {
    setSelectedDocIds((prev) =>
      prev.includes(id) ? prev.filter((d) => d !== id) : [...prev, id]
    );
  };

  const handleSelectAllDocs = () => {
    if (selectedDocIds.length === documents.length) {
      setSelectedDocIds([]);
    } else {
      setSelectedDocIds(documents.map((d) => d.document_id));
    }
  };

  const handleSendMessage = async (text: string) => {
    const userMsg: ChatMessage = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      // Build history for follow-up grounding
      const historyPayload = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const res = await sendChatMessage({
        message: text,
        conversation_history: historyPayload,
        document_ids: selectedDocIds.length > 0 ? selectedDocIds : undefined,
        top_k: topK,
        similarity_threshold: similarityThreshold,
        mode: mode,
      });

      const assistantMsg: ChatMessage = {
        id: `assistant_${Date.now()}`,
        role: 'assistant',
        content: res.answer,
        citations: res.citations,
        timestamp: new Date().toISOString(),
        mode: res.mode,
        agent_steps: res.agent_steps,
      };

      setMessages((prev) => [...prev, assistantMsg]);

      // Update follow-up question chips
      if (res.suggested_followups && res.suggested_followups.length > 0) {
        setSuggestedQuestions(res.suggested_followups);
      }
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `err_${Date.now()}`,
        role: 'assistant',
        content: `⚠️ **Error:** ${err.message || 'Failed to fetch answer. Please check backend connection.'}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = async () => {
    try {
      await clearChat();
    } catch (e) {
      console.warn('Clear chat endpoint warning:', e);
    }
    setMessages([]);
    setSuggestedQuestions([]);
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 text-slate-100">
      <Sidebar
        documents={documents}
        selectedDocIds={selectedDocIds}
        onToggleDocSelection={handleToggleDocSelection}
        onSelectAllDocs={handleSelectAllDocs}
        onDeleteDocument={handleDeleteDocument}
        onUpload={handleUpload}
        isUploading={isUploading}
        health={health}
      />

      <ChatWindow
        messages={messages}
        onSendMessage={handleSendMessage}
        onClearChat={handleClearChat}
        isLoading={isLoading}
        onOpenSettings={() => setIsSettingsOpen(true)}
        mode={mode}
        onToggleMode={() => setMode((m) => (m === 'standard' ? 'agent' : 'standard'))}
        suggestedQuestions={suggestedQuestions}
        hasDocuments={documents.length > 0}
      />

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        topK={topK}
        setTopK={setTopK}
        similarityThreshold={similarityThreshold}
        setSimilarityThreshold={setSimilarityThreshold}
        mode={mode}
        setMode={setMode}
      />
    </div>
  );
};

export default App;
