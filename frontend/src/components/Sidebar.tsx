import React from 'react';
import {
  Trash2,
  Database,
  Cpu,
  Layers,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  FolderOpen
} from 'lucide-react';
import type { DocumentInfo, HealthStatus } from '../types';
import { FileUpload } from './FileUpload';

interface SidebarProps {
  documents: DocumentInfo[];
  selectedDocIds: string[];
  onToggleDocSelection: (id: string) => void;
  onSelectAllDocs: () => void;
  onDeleteDocument: (id: string) => Promise<void>;
  onUpload: (files: File[]) => Promise<void>;
  isUploading: boolean;
  health: HealthStatus | null;
}

export const Sidebar: React.FC<SidebarProps> = ({
  documents,
  selectedDocIds,
  onToggleDocSelection,
  onSelectAllDocs,
  onDeleteDocument,
  onUpload,
  isUploading,
  health,
}) => {
  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const getFileBadge = (fileType: string) => {
    switch (fileType.toLowerCase()) {
      case 'pdf':
        return { color: 'text-rose-400 bg-rose-500/10 border-rose-500/20', label: 'PDF' };
      case 'docx':
        return { color: 'text-blue-400 bg-blue-500/10 border-blue-500/20', label: 'DOCX' };
      default:
        return { color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20', label: 'TXT' };
    }
  };

  return (
    <aside className="w-80 h-full flex flex-col bg-slate-950/80 border-r border-slate-800/80 backdrop-blur-md">
      {/* App Branding */}
      <div className="p-4 border-b border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/25">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-sm tracking-tight text-white flex items-center gap-1.5">
              DocuMind <span className="text-[10px] bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 font-mono px-1.5 py-0.5 rounded">RAG</span>
            </h1>
            <p className="text-[11px] text-slate-400">Contextual Q&A with Citations</p>
          </div>
        </div>
      </div>

      {/* Upload Dropzone */}
      <div className="p-4 border-b border-slate-800/80">
        <FileUpload onUpload={onUpload} isUploading={isUploading} />
      </div>

      {/* Documents List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
          <div className="flex items-center gap-1.5 font-medium text-slate-300">
            <FolderOpen className="w-3.5 h-3.5 text-indigo-400" />
            <span>Indexed Documents</span>
            <span className="text-[11px] font-mono px-1.5 py-0.2 rounded-full bg-slate-800 text-slate-300">
              {documents.length}
            </span>
          </div>

          {documents.length > 0 && (
            <button
              onClick={onSelectAllDocs}
              className="text-[11px] text-indigo-400 hover:text-indigo-300 transition-colors"
            >
              {selectedDocIds.length === documents.length ? 'Clear filter' : 'Filter all'}
            </button>
          )}
        </div>

        {documents.length === 0 ? (
          <div className="text-center py-8 text-slate-500">
            <Layers className="w-8 h-8 mx-auto mb-2 opacity-40 text-slate-400" />
            <p className="text-xs">No documents uploaded</p>
            <p className="text-[11px] text-slate-600 mt-1">Upload files above to begin semantic retrieval</p>
          </div>
        ) : (
          documents.map((doc) => {
            const badge = getFileBadge(doc.file_type);
            const isSelected = selectedDocIds.includes(doc.document_id);

            return (
              <div
                key={doc.document_id}
                className={`p-3 rounded-xl border transition-all duration-200 group relative ${
                  isSelected
                    ? 'border-indigo-500/60 bg-indigo-950/20'
                    : 'border-slate-800 bg-slate-900/40 hover:bg-slate-900/80 hover:border-slate-700'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div
                    onClick={() => onToggleDocSelection(doc.document_id)}
                    className="flex items-start gap-2.5 min-w-0 cursor-pointer flex-1"
                  >
                    <div className="pt-0.5">
                      <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${badge.color}`}>
                        {badge.label}
                      </span>
                    </div>

                    <div className="min-w-0 flex-1">
                      <p className="text-xs font-medium text-slate-200 truncate group-hover:text-indigo-300 transition-colors" title={doc.filename}>
                        {doc.filename}
                      </p>
                      <div className="flex items-center gap-2 text-[10px] text-slate-400 mt-1 font-mono">
                        <span>{formatBytes(doc.file_size_bytes)}</span>
                        <span>•</span>
                        <span>{doc.total_pages} {doc.total_pages === 1 ? 'page' : 'pages'}</span>
                        <span>•</span>
                        <span>{doc.chunk_count} chunks</span>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => onDeleteDocument(doc.document_id)}
                    title="Delete document and vector chunks"
                    className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded transition-all"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* System Status Footer */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-950 text-[11px] text-slate-400 space-y-1.5 font-mono">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <Database className="w-3.5 h-3.5 text-indigo-400" />
            <span>ChromaDB</span>
          </div>
          <span className="flex items-center gap-1 text-emerald-400 text-[10px]">
            <CheckCircle2 className="w-3 h-3" />
            Connected ({health?.total_chunks ?? 0} chunks)
          </span>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-violet-400" />
            <span>Gemini Engine</span>
          </div>
          {health?.gemini_configured ? (
            <span className="flex items-center gap-1 text-emerald-400 text-[10px]">
              <CheckCircle2 className="w-3 h-3" />
              API Active
            </span>
          ) : (
            <span className="flex items-center gap-1 text-amber-400 text-[10px]" title="Add GEMINI_API_KEY to backend/.env">
              <AlertTriangle className="w-3 h-3" />
              Local Fallback
            </span>
          )}
        </div>
      </div>
    </aside>
  );
};
