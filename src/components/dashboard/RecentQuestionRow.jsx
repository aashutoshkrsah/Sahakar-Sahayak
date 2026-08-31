import React from 'react';
import { MessageSquare, ArrowRight, Calendar } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const RecentQuestionRow = ({ question, category, date, chatId }) => {
  const navigate = useNavigate();

  const handleContinue = () => {
    navigate('/chat', { state: { resumeChatId: chatId } });
  };

  const formatDate = (dateString) => {
    if (!dateString) return "";
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  return (
    <div className="flex items-center justify-between p-3.5 bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors group">
      <div className="flex items-center gap-3.5 min-w-0">
        <div className="p-2 rounded-lg bg-slate-50 dark:bg-slate-950 text-slate-400 dark:text-slate-500 shrink-0">
          <MessageSquare className="h-4.5 w-4.5" />
        </div>
        <div className="min-w-0">
          <p className="text-xs font-semibold text-slate-800 dark:text-slate-200 truncate leading-snug">
            {question}
          </p>
          <div className="flex items-center gap-2.5 mt-1 text-[10px] text-slate-400 dark:text-slate-500">
            <span className="bg-slate-100 dark:bg-slate-950 px-2 py-0.5 rounded-full font-medium">
              {category}
            </span>
            <span className="flex items-center gap-1">
              <Calendar className="h-3 w-3" />
              {formatDate(date)}
            </span>
          </div>
        </div>
      </div>

      <button
        onClick={handleContinue}
        className="p-2 rounded-lg text-slate-400 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-slate-100 dark:hover:bg-slate-800 shrink-0 transition-all group-hover:translate-x-1"
        title="Continue Conversation"
        aria-label="Continue Conversation"
      >
        <ArrowRight className="h-4.5 w-4.5" />
      </button>
    </div>
  );
};
export default RecentQuestionRow;
