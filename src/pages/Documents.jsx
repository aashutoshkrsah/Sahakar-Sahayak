import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/AppContext';
import { LayoutWrapper } from '../components/layout/LayoutWrapper';
import { DocumentChecklist } from '../components/resources/DocumentChecklist';
import { documentService } from '../services/documentService';
import { ClipboardCheck, Sparkles } from 'lucide-react';

export const Documents = () => {
  const { t } = useLanguage();
  const [processes, setProcesses] = useState([]);
  const [selectedProcessId, setSelectedProcessId] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchProcesses = async () => {
      setIsLoading(true);
      try {
        const data = await documentService.getProcesses();
        setProcesses(data);
        if (data.length > 0) {
          // Set initial process
          setSelectedProcessId(data[0].id);
        }
      } catch (err) {
        console.error("Failed to load document checklists:", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchProcesses();
  }, []);

  const activeProcess = processes.find(p => p.id === selectedProcessId);

  return (
    <LayoutWrapper title={t('documents')}>
      <div className="space-y-6 text-left animate-message-appear">
        
        {/* Header Title */}
        <div>
          <h2 className="text-xl font-bold font-display text-slate-800 dark:text-white">
            {t('documents')}
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            {t('docDescription')}
          </p>
        </div>

        {isLoading ? (
          <div className="py-12 text-center text-slate-500">
            <span className="inline-block h-6 w-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></span>
            <p className="text-xs font-semibold mt-2">Loading checklists...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            
            {/* Process Selection Sidebar */}
            <div className="lg:col-span-4 bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 rounded-2xl p-4 sm:p-5 shadow-sm space-y-3 transition-colors">
              <h3 className="text-xs font-bold font-display text-slate-400 dark:text-slate-555 uppercase tracking-wider px-2">
                {t('selectProcess')}
              </h3>
              
              <div className="space-y-1">
                {processes.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => setSelectedProcessId(p.id)}
                    className={`w-full text-left px-3 py-2.5 rounded-xl text-xs font-semibold transition-all flex items-center justify-between group cursor-pointer ${
                      selectedProcessId === p.id
                        ? 'bg-primary-600 text-white shadow-sm shadow-primary-500/5'
                        : 'text-slate-650 dark:text-slate-350 hover:bg-slate-50 dark:hover:bg-slate-800'
                    }`}
                  >
                    <span>{p.title}</span>
                    <ClipboardCheck className={`h-4 w-4 shrink-0 transition-opacity ${
                      selectedProcessId === p.id ? 'opacity-100' : 'opacity-0 group-hover:opacity-40'
                    }`} />
                  </button>
                ))}
              </div>
            </div>

            {/* Checklist View Container */}
            <div className="lg:col-span-8">
              {activeProcess ? (
                <DocumentChecklist
                  title={activeProcess.title}
                  description={activeProcess.description}
                  checklistItems={activeProcess.checklist}
                  processId={activeProcess.id}
                />
              ) : (
                <div className="p-8 text-center bg-white dark:bg-slate-900 border border-slate-200/50 dark:border-slate-850 rounded-2xl">
                  <Sparkles className="h-10 w-10 text-slate-400 mx-auto mb-3" />
                  <p className="text-sm font-semibold text-slate-700 dark:text-slate-350">Select a process to view document requirements</p>
                </div>
              )}
            </div>

          </div>
        )}

      </div>
    </LayoutWrapper>
  );
};
export default Documents;
