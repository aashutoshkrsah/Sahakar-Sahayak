import React from 'react';
import { HelpCircle, ArrowRight } from 'lucide-react';

export const EmptyState = ({ 
  title, 
  description, 
  actionText, 
  onActionClick, 
  icon: Icon = HelpCircle 
}) => {
  return (
    <div className="flex flex-col items-center justify-center text-center p-8 bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 rounded-2xl shadow-sm max-w-lg mx-auto">
      <div className="h-16 w-16 rounded-full bg-slate-50 dark:bg-slate-950 flex items-center justify-center text-slate-400 dark:text-slate-500 mb-5 border border-slate-100 dark:border-slate-800">
        <Icon className="h-8 w-8" />
      </div>
      <h3 className="text-base font-bold font-display text-slate-800 dark:text-white mb-2">
        {title}
      </h3>
      <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mb-6 leading-relaxed">
        {description}
      </p>
      {actionText && onActionClick && (
        <button
          onClick={onActionClick}
          className="inline-flex items-center gap-1.5 px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 dark:bg-primary-600 dark:hover:bg-primary-700 shadow-sm transition-colors"
        >
          {actionText}
          <ArrowRight className="h-4 w-4" />
        </button>
      )}
    </div>
  );
};
export default EmptyState;
