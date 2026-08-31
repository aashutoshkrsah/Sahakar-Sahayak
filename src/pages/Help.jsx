import React, { useState } from 'react';
import { useLanguage, useAppData } from '../context/AppContext';
import { LayoutWrapper } from '../components/layout/LayoutWrapper';
import { faqData } from '../data/mockData';
import { 
  HelpCircle, 
  ChevronDown, 
  ChevronUp, 
  Mail, 
  Phone, 
  MapPin, 
  Send,
  AlertTriangle,
  X,
  FileWarning
} from 'lucide-react';

export const Help = () => {
  const { t } = useLanguage();
  const { showToast } = useAppData();

  const [expandedFaqIdx, setExpandedFaqIdx] = useState(null);
  const [reportModalOpen, setReportModalOpen] = useState(false);

  // Form Fields for Report
  const [queryTopic, setQueryTopic] = useState("");
  const [incorrectDetails, setIncorrectDetails] = useState("");
  const [suggestedCorrection, setSuggestedCorrection] = useState("");

  const toggleFaq = (idx) => {
    setExpandedFaqIdx(expandedFaqIdx === idx ? null : idx);
  };

  const handleReportSubmit = (e) => {
    e.preventDefault();
    if (!queryTopic.trim() || !incorrectDetails.trim()) {
      showToast("Please fill in the required fields.", "error");
      return;
    }

    // Mock submission
    console.log("Incorrect Answer Report Submitted:", { queryTopic, incorrectDetails, suggestedCorrection });
    showToast("Feedback submitted. Thank you for maintaining resource accuracy!", "success");
    
    // Reset state & Close
    setQueryTopic("");
    setIncorrectDetails("");
    setSuggestedCorrection("");
    setReportModalOpen(false);
  };

  return (
    <LayoutWrapper title={t('helpSupport')}>
      <div className="space-y-6 text-left animate-message-appear relative">
        
        {/* Title */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h2 className="text-xl font-bold font-display text-slate-800 dark:text-white">
              {t('helpTitle')}
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              {t('helpSubtitle')}
            </p>
          </div>

          <button
            onClick={() => setReportModalOpen(true)}
            className="inline-flex items-center gap-1.5 px-4 py-2 border border-transparent rounded-lg text-xs font-bold text-white bg-amber-500 hover:bg-amber-600 shadow-md shadow-amber-500/10 transition-all hover:translate-y-[-1px] cursor-pointer"
          >
            <AlertTriangle className="h-4 w-4" />
            <span>Report Incorrect Answer</span>
          </button>
        </div>

        {/* Two Column Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Left Column: FAQ Accordion list */}
          <div className="lg:col-span-2 space-y-4">
            <h3 className="text-sm font-bold font-display text-slate-800 dark:text-white">
              {t('faqTitle')}
            </h3>
            
            <div className="space-y-3">
              {faqData.map((faq, idx) => {
                const isExpanded = expandedFaqIdx === idx;
                return (
                  <div 
                    key={idx}
                    onClick={() => toggleFaq(idx)}
                    className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-sm overflow-hidden transition-colors cursor-pointer"
                  >
                    <div className="p-4 sm:p-5 flex justify-between items-center gap-4">
                      <span className="text-xs sm:text-sm font-bold text-slate-800 dark:text-slate-250">
                        {faq.question}
                      </span>
                      <div className="text-slate-400">
                        {isExpanded ? <ChevronUp className="h-4.5 w-4.5" /> : <ChevronDown className="h-4.5 w-4.5" />}
                      </div>
                    </div>

                    {isExpanded && (
                      <div className="px-5 pb-5 pt-3 border-t border-slate-100 dark:border-slate-850 bg-slate-50/40 dark:bg-slate-900/50 text-xs sm:text-sm text-slate-500 dark:text-slate-400 leading-relaxed whitespace-pre-wrap animate-message-appear">
                        {faq.answer}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right Column: Contact Details / Guidelines */}
          <div className="space-y-6">
            
            {/* Quick Tutorial Guide */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-3.5 transition-colors">
              <h3 className="text-xs font-bold font-display text-slate-450 dark:text-slate-550 uppercase tracking-wider">
                How to use the Platform
              </h3>
              <ul className="space-y-3 text-[11px] sm:text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                <li className="flex gap-2">
                  <span className="h-5 w-5 bg-primary-50 dark:bg-primary-950 text-primary-655 font-bold rounded flex items-center justify-center shrink-0">1</span>
                  <span>Select your language from the selector dropdown.</span>
                </li>
                <li className="flex gap-2">
                  <span className="h-5 w-5 bg-primary-50 dark:bg-primary-950 text-primary-655 font-bold rounded flex items-center justify-center shrink-0">2</span>
                  <span>Ask natural language questions to **Sahayak** in English, Nepali, or Hindi.</span>
                </li>
                <li className="flex gap-2">
                  <span className="h-5 w-5 bg-primary-50 dark:bg-primary-950 text-primary-655 font-bold rounded flex items-center justify-center shrink-0">3</span>
                  <span>Verify answers using the embedded references and source cards.</span>
                </li>
                <li className="flex gap-2">
                  <span className="h-5 w-5 bg-primary-50 dark:bg-primary-950 text-primary-655 font-bold rounded flex items-center justify-center shrink-0">4</span>
                  <span>Use checkboxes under **Document Guidance** to track registration steps.</span>
                </li>
              </ul>
            </div>

            {/* Support Channels */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-4 transition-colors">
              <h3 className="text-xs font-bold font-display text-slate-450 dark:text-slate-550 uppercase tracking-wider">
                Support Channels
              </h3>
              
              <div className="space-y-3 text-xs">
                <div className="flex gap-3 items-center">
                  <Mail className="h-4.5 w-4.5 text-primary-600 dark:text-primary-400 shrink-0" />
                  <div>
                    <p className="font-semibold text-slate-700 dark:text-slate-300">Email Support</p>
                    <a href="mailto:support@sahakarsahayak.gov.np" className="text-[11px] text-slate-450 dark:text-slate-500 hover:underline">support@sahakarsahayak.gov.np</a>
                  </div>
                </div>
                
                <div className="flex gap-3 items-center">
                  <Phone className="h-4.5 w-4.5 text-primary-600 dark:text-primary-400 shrink-0" />
                  <div>
                    <p className="font-semibold text-slate-700 dark:text-slate-350">Helpline Phone</p>
                    <p className="text-[11px] text-slate-450 dark:text-slate-500">+977-1-4200000</p>
                  </div>
                </div>

                <div className="flex gap-3 items-center">
                  <MapPin className="h-4.5 w-4.5 text-primary-600 dark:text-primary-400 shrink-0" />
                  <div>
                    <p className="font-semibold text-slate-700 dark:text-slate-350">Administrative Division</p>
                    <p className="text-[11px] text-slate-450 dark:text-slate-500">Ministry of Cooperatives, Kathmandu, Nepal</p>
                  </div>
                </div>
              </div>
            </div>

          </div>

        </div>

        {/* Modal: Report Incorrect Answer */}
        {reportModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" onClick={() => setReportModalOpen(false)} />
            
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-5 sm:p-6 w-full max-w-lg shadow-xl relative z-10 animate-message-appear text-left space-y-4">
              <div className="flex justify-between items-center pb-3 border-b border-slate-100 dark:border-slate-850">
                <h3 className="text-sm sm:text-base font-bold font-display text-slate-800 dark:text-white flex items-center gap-2">
                  <FileWarning className="h-5 w-5 text-amber-500" />
                  <span>Report Incorrect Information</span>
                </h3>
                <button 
                  onClick={() => setReportModalOpen(false)}
                  className="p-1 rounded-md text-slate-450 hover:text-slate-700 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <div className="p-3 bg-amber-50 dark:bg-amber-955/10 border border-amber-200/50 dark:border-amber-900/35 rounded-xl text-[10px] sm:text-xs text-amber-850 dark:text-amber-300 leading-relaxed">
                Legal and cooperative regulatory content must be verified. Let us know what needs correcting, and we will cross-reference the text with municipal guidelines.
              </div>

              <form onSubmit={handleReportSubmit} className="space-y-4 pt-1">
                {/* Topic / Question Input */}
                <div className="space-y-1">
                  <label htmlFor="topic" className="block text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                    Which question/topic is this about? <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="topic"
                    type="text"
                    required
                    value={queryTopic}
                    onChange={(e) => setQueryTopic(e.target.value)}
                    placeholder="e.g. Cooperative Registration Minimum Members"
                    className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-205 dark:border-slate-800 rounded-lg text-slate-800 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 dark:focus:border-primary-400 text-xs sm:text-sm"
                  />
                </div>

                {/* Incorrect Details */}
                <div className="space-y-1">
                  <label htmlFor="details" className="block text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                    Describe the incorrect answer details <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    id="details"
                    required
                    rows={3}
                    value={incorrectDetails}
                    onChange={(e) => setIncorrectDetails(e.target.value)}
                    placeholder="Provide details about what Sahayak got wrong..."
                    className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-955 border border-slate-205 dark:border-slate-800 rounded-lg text-slate-800 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 dark:focus:border-primary-400 text-xs sm:text-sm resize-none"
                  />
                </div>

                {/* Suggested Corrections */}
                <div className="space-y-1">
                  <label htmlFor="correction" className="block text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                    Suggested Correction or Reference (Optional)
                  </label>
                  <textarea
                    id="correction"
                    rows={2}
                    value={suggestedCorrection}
                    onChange={(e) => setSuggestedCorrection(e.target.value)}
                    placeholder="Specify correct laws, document sections, or municipal codes..."
                    className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-955 border border-slate-205 dark:border-slate-800 rounded-lg text-slate-800 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 dark:focus:border-primary-400 text-xs sm:text-sm resize-none"
                  />
                </div>

                {/* Submit button */}
                <div className="flex justify-end gap-3 pt-3 border-t border-slate-100 dark:border-slate-850">
                  <button
                    type="button"
                    onClick={() => setReportModalOpen(false)}
                    className="px-4 py-2 border border-slate-200 dark:border-slate-800 rounded-lg text-xs font-bold text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="inline-flex items-center gap-1.5 px-4 py-2 border border-transparent rounded-lg text-xs font-bold text-white bg-primary-600 hover:bg-primary-700 shadow-sm"
                  >
                    <Send className="h-3.5 w-3.5" />
                    <span>Submit Report</span>
                  </button>
                </div>
              </form>

            </div>
          </div>
        )}

      </div>
    </LayoutWrapper>
  );
};
export default Help;
