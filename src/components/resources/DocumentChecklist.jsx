import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle2, MessageSquare, ArrowRight, ClipboardList } from 'lucide-react';
import { useLanguage } from '../../context/AppContext';

export const DocumentChecklist = ({ title, description, checklistItems, processId }) => {
  const { t } = useLanguage();
  const navigate = useNavigate();
  
  // Track checked state locally
  const [checkedStates, setCheckedStates] = useState({});

  // Reset checked states when process changes
  useEffect(() => {
    const initial = {};
    checklistItems.forEach(item => {
      initial[item.id] = false;
    });
    setCheckedStates(initial);
  }, [checklistItems]);

  const toggleCheck = (id) => {
    setCheckedStates(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const checkedCount = Object.values(checkedStates).filter(Boolean).length;
  const totalCount = checklistItems.length;
  const completionPercent = totalCount > 0 ? Math.round((checkedCount / totalCount) * 100) : 0;

  const handleAskSahayak = () => {
    // Generate context message
    const docNames = checklistItems.map(d => d.name).join(", ");
    const textPrompt = `Help me understand the documents required for ${title}. Specifically, what do I need to prepare for: ${docNames}?`;
    
    // Navigate to chat and pre-fill
    navigate('/chat', { state: { initialQuery: textPrompt, initialCategory: 'Documents' } });
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl p-5 sm:p-6 shadow-sm space-y-5 transition-colors">
      
      {/* Title & Desc */}
      <div className="flex gap-4 items-start pb-4 border-b border-slate-100 dark:border-slate-850">
        <div className="p-3 bg-primary-50 dark:bg-primary-950/40 text-primary-600 dark:text-primary-400 rounded-xl shrink-0">
          <ClipboardList className="h-6 w-6" />
        </div>
        <div>
          <h3 className="text-base font-bold font-display text-slate-850 dark:text-white leading-snug">
            {title}
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed mt-1">
            {description}
          </p>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between items-center text-xs">
          <span className="font-semibold text-slate-700 dark:text-slate-350">
            Document Preparation Progress
          </span>
          <span className="font-bold text-primary-600 dark:text-primary-400">
            {checkedCount} / {totalCount} ({completionPercent}%)
          </span>
        </div>
        <div className="w-full bg-slate-100 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
          <div 
            className="bg-primary-600 dark:bg-primary-500 h-full rounded-full transition-all duration-300"
            style={{ width: `${completionPercent}%` }}
          />
        </div>
      </div>

      {/* Checklist Grid */}
      <div className="space-y-3">
        <h4 className="text-xs font-bold text-slate-400 dark:text-slate-550 uppercase tracking-wider">
          {t('requiredDocsChecklist')}
        </h4>
        <div className="space-y-2.5">
          {checklistItems.map((item) => (
            <div 
              key={item.id}
              onClick={() => toggleCheck(item.id)}
              className={`flex items-start gap-3.5 p-3 rounded-xl border transition-all cursor-pointer ${
                checkedStates[item.id]
                  ? 'border-emerald-250 dark:border-emerald-900/60 bg-emerald-50/20 dark:bg-emerald-950/10'
                  : 'border-slate-200/80 dark:border-slate-800 bg-slate-50/30 dark:bg-slate-900/30 hover:bg-slate-50 dark:hover:bg-slate-900'
              }`}
            >
              {/* Custom Checkbox */}
              <button
                type="button"
                className={`h-5 w-5 rounded border flex items-center justify-center shrink-0 mt-0.5 transition-colors ${
                  checkedStates[item.id]
                    ? 'bg-emerald-500 border-emerald-500 text-white'
                    : 'border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900'
                }`}
                aria-label={`Toggle ${item.name}`}
              >
                {checkedStates[item.id] && <CheckCircle2 className="h-4 w-4 fill-emerald-500 text-white" />}
              </button>

              {/* Text info */}
              <div className="min-w-0 flex-1 select-none">
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-semibold leading-tight ${checkedStates[item.id] ? 'text-slate-800 dark:text-slate-200 line-through opacity-70' : 'text-slate-800 dark:text-slate-200'}`}>
                    {item.name}
                  </span>
                  {item.required ? (
                    <span className="text-[9px] font-bold text-red-500 dark:text-red-400 bg-red-50 dark:bg-red-950/10 px-1.5 py-0.2 rounded uppercase">
                      Required
                    </span>
                  ) : (
                    <span className="text-[9px] font-bold text-slate-400 dark:text-slate-500 bg-slate-100 dark:bg-slate-850 px-1.5 py-0.2 rounded uppercase">
                      Optional
                    </span>
                  )}
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed mt-1">
                  {item.desc}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* CTA Button */}
      <button
        onClick={handleAskSahayak}
        className="w-full inline-flex items-center justify-center gap-2 py-3 border border-transparent rounded-xl text-sm font-bold text-white bg-primary-600 hover:bg-primary-700 dark:bg-primary-600 dark:hover:bg-primary-700 shadow-md shadow-primary-500/10 transition-all hover:translate-y-[-1px] active:translate-y-0"
      >
        <MessageSquare className="h-4 w-4" />
        <span>{t('askSahayakAboutDocs')}</span>
        <ArrowRight className="h-4 w-4" />
      </button>

    </div>
  );
};
export default DocumentChecklist;
