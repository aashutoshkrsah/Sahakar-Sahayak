import React from 'react';

export const SuggestionChip = ({ label, onClick, className = "" }) => {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-1.5 bg-slate-50 hover:bg-primary-50 dark:bg-slate-900 dark:hover:bg-primary-950/20 text-slate-650 hover:text-primary-650 dark:text-slate-300 dark:hover:text-primary-400 border border-slate-200 hover:border-primary-200 dark:border-slate-800 dark:hover:border-primary-900/50 rounded-full text-xs font-medium transition-all cursor-pointer ${className}`}
    >
      {label}
    </button>
  );
};
export default SuggestionChip;
