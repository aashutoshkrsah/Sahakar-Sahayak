import React, { useState } from 'react';
import { useLanguage, useAppData } from '../context/AppContext';
import { LayoutWrapper } from '../components/layout/LayoutWrapper';
import { SearchBar } from '../components/common/SearchBar';
import { EmptyState } from '../components/common/EmptyState';
import { Bookmark, MessageSquare, Trash2, Calendar, ChevronDown, ChevronUp } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const SavedAnswers = () => {
  const { t } = useLanguage();
  const { savedAnswers, toggleSaveAnswer } = useAppData();
  const navigate = useNavigate();

  const [searchQuery, setSearchQuery] = useState("");
  const [expandedId, setExpandedId] = useState(null);

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const handleOpenConversation = (question) => {
    navigate('/chat', { state: { initialQuery: question } });
  };

  const handleRemove = (e, item) => {
    e.stopPropagation();
    toggleSaveAnswer(item.question, item.answer, item.category, item.sources);
  };

  // Filter bookmarked answers
  const filteredAnswers = savedAnswers.filter(sa => {
    if (!searchQuery) return true;
    const lowerQuery = searchQuery.toLowerCase();
    return (
      sa.question.toLowerCase().includes(lowerQuery) ||
      sa.answer.toLowerCase().includes(lowerQuery) ||
      sa.category.toLowerCase().includes(lowerQuery)
    );
  });

  const formatDate = (dateString) => {
    if (!dateString) return "";
    return new Date(dateString).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
  };

  return (
    <LayoutWrapper title={t('savedAnswers')}>
      <div className="space-y-6 text-left animate-message-appear">
        
        {/* Title */}
        <div>
          <h2 className="text-xl font-bold font-display text-slate-800 dark:text-white">
            {t('savedAnswers')}
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Browse and query answers you bookmarked during your AI chat sessions.
          </p>
        </div>

        {savedAnswers.length === 0 ? (
          /* Empty State */
          <EmptyState
            title="No Bookmarked Answers Yet"
            description="When chatting with Sahayak, click the bookmark icon on any response to save it here for offline viewing."
            actionText={t('askFirstQuestion')}
            onActionClick={() => navigate('/chat')}
            icon={Bookmark}
          />
        ) : (
          <>
            {/* Search Input */}
            <SearchBar
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onClear={() => setSearchQuery("")}
              placeholder="Search in bookmarked answers..."
            />

            {/* List */}
            {filteredAnswers.length === 0 ? (
              <div className="p-8 text-center bg-white dark:bg-slate-900 border border-slate-200/50 dark:border-slate-850 rounded-2xl">
                <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{t('noResultsFound')}</p>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredAnswers.map((item) => {
                  const isExpanded = expandedId === item.id;
                  return (
                    <div 
                      key={item.id}
                      onClick={() => toggleExpand(item.id)}
                      className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-sm overflow-hidden transition-colors cursor-pointer"
                    >
                      {/* Accordion Trigger Header */}
                      <div className="p-4 sm:p-5 flex justify-between items-start gap-4">
                        <div className="min-w-0 flex-1 space-y-2">
                          <div className="flex flex-wrap items-center gap-2.5">
                            <span className="text-[10px] bg-primary-50 dark:bg-primary-950/20 text-primary-750 dark:text-primary-400 px-2 py-0.5 rounded-full font-bold border border-primary-100/40">
                              {item.category}
                            </span>
                            <span className="flex items-center gap-1 text-[10px] text-slate-400 dark:text-slate-500 font-semibold">
                              <Calendar className="h-3.5 w-3.5" />
                              Saved {formatDate(item.savedDate)}
                            </span>
                          </div>
                          
                          <h3 className="text-xs sm:text-sm font-bold text-slate-850 dark:text-white leading-snug truncate-none">
                            {item.question}
                          </h3>
                        </div>

                        {/* Actions buttons */}
                        <div className="flex items-center gap-1.5 shrink-0" onClick={(e) => e.stopPropagation()}>
                          <button
                            onClick={() => handleOpenConversation(item.question)}
                            className="p-1.5 rounded-lg border border-slate-250 dark:border-slate-800 text-slate-500 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
                            title="Ask Sahayak"
                          >
                            <MessageSquare className="h-4.5 w-4.5" />
                          </button>
                          
                          <button
                            onClick={(e) => handleRemove(e, item)}
                            className="p-1.5 rounded-lg border border-slate-250 dark:border-slate-855 text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/10 transition-colors"
                            title="Remove Bookmark"
                          >
                            <Trash2 className="h-4.5 w-4.5" />
                          </button>

                          <div className="text-slate-400 p-1.5">
                            {isExpanded ? <ChevronUp className="h-4.5 w-4.5" /> : <ChevronDown className="h-4.5 w-4.5" />}
                          </div>
                        </div>

                      </div>

                      {/* Expandable answer panel */}
                      {isExpanded && (
                        <div className="px-5 pb-5 border-t border-slate-100 dark:border-slate-850 pt-4 bg-slate-50/40 dark:bg-slate-900/50 text-xs sm:text-sm text-slate-700 dark:text-slate-350 leading-relaxed whitespace-pre-wrap animate-message-appear">
                          {item.answer}

                          {/* Render sources card nested inside bookmark if available */}
                          {item.sources && item.sources.length > 0 && (
                            <div className="mt-4 pt-4 border-t border-slate-200/60 dark:border-slate-800/80">
                              <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-2">
                                Sources
                              </p>
                              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 max-w-lg">
                                {item.sources.map((src, sIdx) => (
                                  <div key={sIdx} className="bg-white dark:bg-slate-950 p-2.5 rounded-xl border border-slate-200/50 dark:border-slate-850 flex justify-between items-center text-[11px] font-semibold text-slate-750 dark:text-slate-300">
                                    <span>{src.documentName}</span>
                                    <span className="text-[10px] text-slate-450 dark:text-slate-500 font-medium">{src.provision}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                    </div>
                  );
                })}
              </div>
            )}
          </>
        )}

      </div>
    </LayoutWrapper>
  );
};
export default SavedAnswers;
