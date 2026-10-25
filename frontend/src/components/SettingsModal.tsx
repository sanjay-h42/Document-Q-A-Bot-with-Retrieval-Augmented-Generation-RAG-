import React from 'react';
import { X, Sliders, Bot, Zap, HelpCircle } from 'lucide-react';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  topK: number;
  setTopK: (val: number) => void;
  similarityThreshold: number;
  setSimilarityThreshold: (val: number) => void;
  mode: 'standard' | 'agent';
  setMode: (mode: 'standard' | 'agent') => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  topK,
  setTopK,
  similarityThreshold,
  setSimilarityThreshold,
  mode,
  setMode,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-md glass-panel rounded-2xl p-6 shadow-2xl border border-slate-700/80">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2 text-white font-semibold">
            <Sliders className="w-5 h-5 text-indigo-400" />
            <span>RAG & Retrieval Settings</span>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-6 pt-5">
          {/* Operation Mode */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Execution Mode
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setMode('standard')}
                className={`p-3 rounded-xl border text-left transition-all ${
                  mode === 'standard'
                    ? 'border-indigo-500 bg-indigo-500/10 text-white ring-1 ring-indigo-500'
                    : 'border-slate-800 bg-slate-900/60 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <Zap className="w-4 h-4 text-indigo-400" />
                  <span className="text-xs font-semibold">Standard RAG</span>
                </div>
                <p className="text-[11px] text-slate-400">
                  Single-hop semantic retrieval with direct source citations.
                </p>
              </button>

              <button
                type="button"
                onClick={() => setMode('agent')}
                className={`p-3 rounded-xl border text-left transition-all ${
                  mode === 'agent'
                    ? 'border-violet-500 bg-violet-500/10 text-white ring-1 ring-violet-500'
                    : 'border-slate-800 bg-slate-900/60 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <Bot className="w-4 h-4 text-violet-400" />
                  <span className="text-xs font-semibold">Research Agent</span>
                </div>
                <p className="text-[11px] text-slate-400">
                  Multi-step bounded reasoning, cross-document comparison & trail.
                </p>
              </button>
            </div>
          </div>

          {/* Top-K Chunks */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
                Top-K Retrieved Chunks
                <span title="Number of most similar text chunks passed to the LLM">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
                </span>
              </label>
              <span className="font-mono text-xs text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded">
                {topK}
              </span>
            </div>
            <input
              type="range"
              min="1"
              max="10"
              step="1"
              value={topK}
              onChange={(e) => setTopK(parseInt(e.target.value, 10))}
              className="w-full accent-indigo-500 bg-slate-800 h-1.5 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 mt-1">
              <span>1 (Precise)</span>
              <span>10 (Comprehensive)</span>
            </div>
          </div>

          {/* Similarity Score Threshold */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
                Similarity Score Cutoff
                <span title="Minimum semantic relevance required for a chunk to be cited">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
                </span>
              </label>
              <span className="font-mono text-xs text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded">
                {Math.round(similarityThreshold * 100)}%
              </span>
            </div>
            <input
              type="range"
              min="0.05"
              max="0.80"
              step="0.05"
              value={similarityThreshold}
              onChange={(e) => setSimilarityThreshold(parseFloat(e.target.value))}
              className="w-full accent-indigo-500 bg-slate-800 h-1.5 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 mt-1">
              <span>5% (Relaxed)</span>
              <span>80% (Strict)</span>
            </div>
          </div>
        </div>

        <div className="mt-6 pt-4 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium rounded-xl shadow-lg shadow-indigo-600/30 transition-all"
          >
            Apply Settings
          </button>
        </div>
      </div>
    </div>
  );
};
