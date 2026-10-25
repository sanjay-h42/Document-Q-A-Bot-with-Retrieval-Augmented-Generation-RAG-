import React, { useState, useRef } from 'react';
import { UploadCloud, AlertCircle, Loader2 } from 'lucide-react';

interface FileUploadProps {
  onUpload: (files: File[]) => Promise<void>;
  isUploading: boolean;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onUpload, isUploading }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const allowedExtensions = ['.pdf', '.docx', '.txt'];
  const maxSizeBytes = 25 * 1024 * 1024; // 25 MB

  const validateAndUpload = async (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) return;
    setErrorMessage(null);

    const validFiles: File[] = [];

    for (let i = 0; i < fileList.length; i++) {
      const file = fileList[i];
      const ext = '.' + file.name.split('.').pop()?.toLowerCase();

      if (!allowedExtensions.includes(ext)) {
        setErrorMessage(`"${file.name}" is not supported. Use PDF, DOCX, or TXT.`);
        return;
      }

      if (file.size > maxSizeBytes) {
        setErrorMessage(`"${file.name}" exceeds the 25MB limit.`);
        return;
      }

      if (file.size === 0) {
        setErrorMessage(`"${file.name}" is empty (0 bytes).`);
        return;
      }

      validFiles.push(file);
    }

    try {
      await onUpload(validFiles);
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to upload files');
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    validateAndUpload(e.dataTransfer.files);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  return (
    <div className="w-full">
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => !isUploading && fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-xl p-4 text-center cursor-pointer transition-all duration-300 ${
          isDragOver
            ? 'border-indigo-400 bg-indigo-500/10 scale-[1.01]'
            : 'border-slate-700/80 hover:border-indigo-500/50 bg-slate-900/40 hover:bg-slate-900/70'
        } ${isUploading ? 'opacity-60 cursor-not-allowed pointer-events-none' : ''}`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.txt"
          className="hidden"
          onChange={(e) => validateAndUpload(e.target.files)}
        />

        <div className="flex flex-col items-center justify-center gap-2">
          <div className="p-2.5 rounded-full bg-indigo-500/10 text-indigo-400">
            {isUploading ? (
              <Loader2 className="w-6 h-6 animate-spin text-indigo-400" />
            ) : (
              <UploadCloud className="w-6 h-6" />
            )}
          </div>

          <div>
            <p className="text-xs font-medium text-slate-200">
              {isUploading ? 'Processing & Vectorizing Chunks...' : 'Drop PDF, DOCX, TXT files here'}
            </p>
            <p className="text-[11px] text-slate-400 mt-0.5">
              or <span className="text-indigo-400 font-medium hover:underline">browse files</span> (up to 25MB each)
            </p>
          </div>
        </div>
      </div>

      {errorMessage && (
        <div className="mt-2 p-2 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span className="truncate">{errorMessage}</span>
        </div>
      )}
    </div>
  );
};
