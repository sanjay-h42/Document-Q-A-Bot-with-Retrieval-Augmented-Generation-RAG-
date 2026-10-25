import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Send,
  Trash2,
  Sliders,
  Bot,
  User,
  Sparkles,
  Layers,
  ChevronDown,
  ChevronRight,
  ShieldCheck,
  Zap,
  Info
} from 'lucide-react';
import type { ChatMessage } from '../types';
import { CitationCard } from './CitationCard';
import { SuggestedQuestions } from './SuggestedQuestions';

interface ChatWindowProps {
  messages: ChatMessage[];
  onSendMessage: (text: string) => Promise<void>;
  onClearChat: () => Promise<void>;
  isLoading: boolean;
  onOpenSettings: () => void;
  mode: 'standard' | 'agent';
  onToggleMode: () => void;
  suggestedQuestions: string[];
  hasDocuments: boolean;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  onSendMessage,
  onClearChat,
  isLoading,
  onOpenSettings,
  mode,
  onToggleMode,
  suggestedQuestions,
  hasDocuments,
}) => {
  const [inputText, setInputText] = useState('');
  const [expandedSteps, setExpandedSteps] = useState<{ [msgId: string]: boolean }>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputText.trim() || isLoading) return;

    const messageText = inputText.trim();
    setInputText('');
    await onSendMessage(messageText);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const toggleStepAccordion = (msgId: string) => {
    setExpandedSteps((prev) => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  return (
    <div className="flex-1 h-full flex flex-col bg-slate-900/60 relative overflow-hidden">
      {/* Top Navbar */}
      <header className="h-14 border-b border-slate-800/80 px-6 flex items-center justify-between glass-panel z-10">
        <div className="flex items-center gap-3">
          <button
            onClick={onToggleMode}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-all duration-200 ${
              mode === 'agent'
                ? 'bg-violet-500/10 text-violet-300 border-violet-500/40 hover:bg-violet-500/20'
                : 'bg-indigo-500/10 text-indigo-300 border-indigo-500/40 hover:bg-indigo-500/20'
            }`}
            title="Click to toggle between Standard RAG and Multi-Step Research Agent"
          >
            {mode === 'agent' ? <Bot className="w-3.5 h-3.5" /> : <Zap className="w-3.5 h-3.5" />}
            <span>{mode === 'agent' ? 'Research Agent Mode' : 'Standard RAG Mode'}</span>
          </button>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onOpenSettings}
            className="p-2 text-slate-400 hover:text-white hover:bg-slate-800/80 rounded-lg transition-colors"
            title="RAG Parameters & Thresholds"
          >
            <Sliders className="w-4 h-4" />
          </button>

          <button
            onClick={onClearChat}
            disabled={messages.length === 0}
            className="p-2 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors disabled:opacity-30 disabled:pointer-events-none"
            title="Clear Chat History"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6 space-y-6">
        {messages.length === 0 ? (
          <div className="max-w-2xl mx-auto py-12 text-center space-y-8 animate-in fade-in duration-500">
            <div className="inline-flex p-3 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 shadow-xl shadow-indigo-500/10">
              <Sparkles className="w-8 h-8" />
            </div>

            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight">
                Document Q&A with Grounded Citations
              </h2>
              <p className="text-slate-400 text-sm mt-2 max-w-md mx-auto">
                Ask precise questions across your uploaded PDF, DOCX, and TXT files.
                Every response is verified against retrieved chunks with source page citations.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-left">
              <div className="p-4 rounded-xl glass-card border border-slate-800/80">
                <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 w-fit mb-2">
                  <ShieldCheck className="w-4 h-4" />
                </div>
                <h3 className="text-xs font-semibold text-slate-200">Zero Hallucinations</h3>
                <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                  Strict context grounding: if evidence is absent, the system declines to speculate.
                </p>
              </div>

              <div className="p-4 rounded-xl glass-card border border-slate-800/80">
                <div className="p-2 rounded-lg bg-violet-500/10 text-violet-400 w-fit mb-2">
                  <Layers className="w-4 h-4" />
                </div>
                <h3 className="text-xs font-semibold text-slate-200">Multi-Hop Research</h3>
                <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                  Toggle Research Agent to compare concepts across different documents seamlessly.
                </p>
              </div>

              <div className="p-4 rounded-xl glass-card border border-slate-800/80">
                <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 w-fit mb-2">
                  <Info className="w-4 h-4" />
                </div>
                <h3 className="text-xs font-semibold text-slate-200">Exact Page Citations</h3>
                <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                  Inspect matched excerpts, similarity scores, and specific document page numbers.
                </p>
              </div>
            </div>

            {!hasDocuments && (
              <div className="p-3 rounded-xl bg-indigo-950/30 border border-indigo-500/20 text-indigo-300 text-xs inline-block">
                👈 Start by uploading a document in the sidebar to begin.
              </div>
            )}
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 max-w-3xl ${
                msg.role === 'user' ? 'ml-auto flex-row-reverse' : 'mr-auto'
              }`}
            >
              <div
                className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 text-sm shadow-md ${
                  msg.role === 'user'
                    ? 'bg-indigo-600 text-white'
                    : msg.mode === 'agent'
                    ? 'bg-violet-600 text-white'
                    : 'bg-slate-800 text-indigo-400 border border-indigo-500/30'
                }`}
              >
                {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              <div
                className={`min-w-0 max-w-[85%] rounded-2xl p-4 shadow-lg ${
                  msg.role === 'user'
                    ? 'bg-indigo-600 text-white rounded-tr-none'
                    : 'glass-panel text-slate-200 rounded-tl-none border border-slate-700/60'
                }`}
              >
                {/* Agent Thought Trail Accordion */}
                {msg.agent_steps && msg.agent_steps.length > 0 && (
                  <div className="mb-3 border border-violet-500/30 bg-violet-950/20 rounded-xl overflow-hidden">
                    <button
                      type="button"
                      onClick={() => toggleStepAccordion(msg.id)}
                      className="w-full px-3 py-2 text-left flex items-center justify-between text-xs font-medium text-violet-300 hover:bg-violet-900/20 transition-colors"
                    >
                      <span className="flex items-center gap-1.5">
                        <Bot className="w-3.5 h-3.5 text-violet-400" />
                        <span>Agent Reasoning & Retrieval Trail ({msg.agent_steps.length} steps)</span>
                      </span>
                      {expandedSteps[msg.id] ? (
                        <ChevronDown className="w-3.5 h-3.5" />
                      ) : (
                        <ChevronRight className="w-3.5 h-3.5" />
                      )}
                    </button>

                    {expandedSteps[msg.id] && (
                      <div className="px-3 pb-3 pt-1 space-y-1.5 text-[11px] font-mono text-slate-300 border-t border-violet-500/20">
                        {msg.agent_steps.map((step, idx) => (
                          <div key={idx} className="flex items-start gap-2">
                            <span className="text-violet-400 font-bold">{idx + 1}.</span>
                            <span>{step}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Message Content */}
                <div className="prose prose-invert prose-sm max-w-none leading-relaxed text-sm">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.content}
                  </ReactMarkdown>
                </div>

                {/* Citations Grid */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-700/50">
                    <div className="text-[11px] font-semibold text-slate-400 mb-2 flex items-center gap-1.5">
                      <Layers className="w-3.5 h-3.5 text-indigo-400" />
                      <span>Retrieved Source Citations ({msg.citations.length}):</span>
                    </div>
                    <div className="grid grid-cols-1 gap-2">
                      {msg.citations.map((citation, idx) => (
                        <CitationCard key={idx} citation={citation} index={idx + 1} />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex gap-3 max-w-3xl mr-auto animate-in fade-in">
            <div className="w-8 h-8 rounded-xl bg-slate-800 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <Bot className="w-4 h-4 animate-pulse" />
            </div>
            <div className="glass-panel rounded-2xl rounded-tl-none p-4 flex items-center gap-3">
              <div className="flex space-x-1.5">
                <div className="w-2 h-2 rounded-full bg-indigo-500 animate-bounce [animation-delay:-0.3s]"></div>
                <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce [animation-delay:-0.15s]"></div>
                <div className="w-2 h-2 rounded-full bg-violet-400 animate-bounce"></div>
              </div>
              <span className="text-xs text-slate-400 font-mono">
                {mode === 'agent' ? 'Agent evaluating & retrieving multi-step evidence...' : 'Retrieving chunks & generating grounded response...'}
              </span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form & Suggested Questions */}
      <div className="p-4 border-t border-slate-800/80 glass-panel z-10">
        <div className="max-w-3xl mx-auto space-y-2">
          {/* Suggested Prompts */}
          <SuggestedQuestions
            questions={suggestedQuestions}
            onSelectQuestion={(q) => onSendMessage(q)}
          />

          <form onSubmit={handleSubmit} className="relative">
            <textarea
              ref={textareaRef}
              rows={2}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                hasDocuments
                  ? 'Ask a question about the uploaded documents (Shift+Enter for new line)...'
                  : 'Upload documents in the sidebar first to start asking questions...'
              }
              disabled={isLoading}
              className="w-full bg-slate-950/80 border border-slate-700/80 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm text-slate-100 placeholder-slate-500 rounded-xl px-4 py-3 pr-12 resize-none outline-none transition-all"
            />

            <button
              type="submit"
              disabled={!inputText.trim() || isLoading}
              className="absolute right-3 bottom-3.5 p-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:hover:bg-indigo-600 text-white rounded-lg shadow-md transition-all duration-200"
              title="Send Message"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>

          <div className="flex items-center justify-between text-[11px] text-slate-500 px-1">
            <span>Powered by ChromaDB Vector Search & Google Gemini</span>
            <span>Grounding mode: Strict anti-hallucination</span>
          </div>
        </div>
      </div>
    </div>
  );
};
