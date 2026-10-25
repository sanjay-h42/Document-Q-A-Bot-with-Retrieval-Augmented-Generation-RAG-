import React from 'react';
import { Sparkles } from 'lucide-react';

interface SuggestedQuestionsProps {
  questions: string[];
  onSelectQuestion: (question: string) => void;
}

export const SuggestedQuestions: React.FC<SuggestedQuestionsProps> = ({
  questions,
  onSelectQuestion,
}) => {
  if (!questions || questions.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-2 pt-1 pb-2">
      <div className="flex items-center gap-1 text-[11px] font-medium text-indigo-400">
        <Sparkles className="w-3.5 h-3.5" />
        <span>Suggested:</span>
      </div>
      {questions.map((q, idx) => (
        <button
          key={idx}
          onClick={() => onSelectQuestion(q)}
          className="text-xs bg-slate-900/80 hover:bg-indigo-950/60 border border-slate-700/60 hover:border-indigo-500/50 text-slate-300 hover:text-indigo-200 px-2.5 py-1 rounded-full transition-all duration-200 truncate max-w-xs md:max-w-md text-left shadow-sm"
        >
          {q}
        </button>
      ))}
    </div>
  );
};
