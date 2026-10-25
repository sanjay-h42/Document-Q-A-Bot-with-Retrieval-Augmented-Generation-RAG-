import React, { useState } from 'react';
import { FileText, ChevronDown, ChevronUp, Copy, Check } from 'lucide-react';
import type { Citation } from '../types';

interface CitationCardProps {
  citation: Citation;
  index: number;
}

export const CitationCard: React.FC<CitationCardProps> = ({ citation, index }) => {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(citation.excerpt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const scorePercent = Math.round(citation.similarity_score * 100);

  return (
    <div
      onClick={() => setExpanded(!expanded)}
      className="glass-card rounded-lg p-3 cursor-pointer transition-all duration-200 hover:border-indigo-500/50 hover:bg-slate-800/80 group"
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <div className="p-1.5 rounded bg-indigo-500/10 text-indigo-400 group-hover:bg-indigo-500/20 transition-colors">
            <FileText className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <div className="text-xs font-semibold text-slate-200 truncate group-hover:text-indigo-300">
              [{index}] {citation.filename}
            </div>
            <div className="text-[11px] text-slate-400">
              Page {citation.page_number}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          <span
            className={`text-[10px] font-mono px-1.5 py-0.5 rounded-full ${
              scorePercent >= 70
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                : scorePercent >= 45
                ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                : 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'
            }`}
          >
            {scorePercent}% match
          </span>

          <button
            onClick={handleCopy}
            title="Copy source excerpt"
            className="p-1 text-slate-400 hover:text-slate-100 hover:bg-slate-700/50 rounded transition-colors"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>

          <span className="text-slate-400 group-hover:text-slate-200">
            {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </span>
        </div>
      </div>

      <div
        className={`mt-2 text-xs text-slate-300 leading-relaxed font-mono transition-all duration-300 bg-slate-900/60 p-2.5 rounded border border-slate-700/50 ${
          expanded ? 'block' : 'line-clamp-2'
        }`}
      >
        "{citation.excerpt}"
      </div>
    </div>
  );
};
