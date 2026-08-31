import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useLanguage, useAppData } from '../context/AppContext';
import { LayoutWrapper } from '../components/layout/LayoutWrapper';
import { resourceService } from '../services/resourceService';
import { ArrowLeft, MessageSquare, Download, Calendar, Scale, ChevronRight } from 'lucide-react';

export const ResourceDetails = () => {
  const { id } = useParams();
  const { t } = useLanguage();
  const { showToast } = useAppData();
  const navigate = useNavigate();

  const [resource, setResource] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchResource = async () => {
      setIsLoading(true);
      try {
        const data = await resourceService.getResourceById(id);
        setResource(data);
      } catch (err) {
        console.error("Failed to load resource details:", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchResource();
  }, [id]);

  const handleDownload = () => {
    showToast(`PDF download initiated for ${resource?.title || "document"}`);
  };

  const handleAskSahayak = () => {
    if (!resource) return;
    const textPrompt = `Ask me anything about: ${resource.title}. Specifically, what does this document cover?`;
    navigate('/chat', { state: { initialQuery: textPrompt, initialCategory: 'Legal Resources' } });
  };

  if (isLoading) {
    return (
      <LayoutWrapper title="Legal Documents">
        <div className="py-12 text-center text-slate-500">
          <span className="inline-block h-6 w-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></span>
          <p className="text-xs font-semibold mt-2">Opening legislative archive...</p>
        </div>
      </LayoutWrapper>
    );
  }

  if (!resource) {
    return (
      <LayoutWrapper title="Document Not Found">
        <div className="py-12 text-center bg-white dark:bg-slate-900 border border-slate-200/50 dark:border-slate-850 rounded-2xl max-w-md mx-auto space-y-4 text-left p-6">
          <Scale className="h-10 w-10 text-slate-400 mx-auto" />
          <h3 className="text-sm font-bold font-display text-slate-800 dark:text-white text-center">
            Resource Not Found
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 text-center leading-relaxed">
            The requested cooperative act or regulatory guideline does not exist or has been archived.
          </p>
          <div className="text-center">
            <Link 
              to="/resources"
              className="inline-flex items-center gap-1.5 text-xs font-bold text-primary-655 hover:underline"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back to Resources</span>
            </Link>
          </div>
        </div>
      </LayoutWrapper>
    );
  }

  return (
    <LayoutWrapper title={resource.title}>
      <div className="space-y-6 text-left animate-message-appear">
        
        {/* Navigation Toolbar */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-4 rounded-2xl shadow-sm transition-colors">
          <Link
            to="/resources"
            className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-white transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back to Legal Library</span>
          </Link>
          
          <div className="flex flex-wrap items-center gap-3">
            {/* Download Button */}
            <button
              onClick={handleDownload}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 border border-slate-250 dark:border-slate-800 bg-white dark:bg-slate-900 rounded-lg text-xs font-semibold text-slate-700 dark:text-slate-250 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors cursor-pointer"
            >
              <Download className="h-4 w-4 text-slate-400" />
              <span>Download PDF</span>
            </button>

            {/* Ask Sahayak CTA */}
            <button
              onClick={handleAskSahayak}
              className="inline-flex items-center gap-1.5 px-4 py-2 border border-transparent rounded-lg text-xs font-bold text-white bg-primary-600 hover:bg-primary-700 dark:bg-primary-600 dark:hover:bg-primary-700 shadow-md shadow-primary-500/10 transition-all hover:translate-y-[-1px] active:translate-y-0 cursor-pointer"
            >
              <MessageSquare className="h-4 w-4" />
              <span>Ask Sahayak About This</span>
            </button>
          </div>
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          
          {/* Main Document Content */}
          <div className="lg:col-span-8 bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 rounded-3xl p-6 sm:p-8 shadow-sm space-y-6 transition-colors">
            
            {/* Document Header Metadata */}
            <div className="space-y-3 pb-5 border-b border-slate-100 dark:border-slate-850">
              <div className="flex items-center gap-2.5">
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 border border-primary-100 bg-primary-50 dark:bg-primary-950/20 text-primary-600 dark:text-primary-400 rounded-full">
                  {resource.category}
                </span>
                <span className="inline-flex items-center gap-1.5 text-[10px] text-slate-400 dark:text-slate-500 font-semibold">
                  <Calendar className="h-3.5 w-3.5" />
                  Last Updated: {resource.lastUpdated}
                </span>
              </div>
              <h2 className="text-xl sm:text-2xl font-black font-display text-slate-855 dark:text-white leading-tight">
                {resource.title}
              </h2>
            </div>

            {/* Overview */}
            <div className="space-y-2">
              <h3 className="text-sm font-bold font-display text-slate-800 dark:text-slate-250">
                Document Overview
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed bg-slate-50 dark:bg-slate-950 p-4 rounded-2xl border border-slate-200/40 dark:border-slate-850">
                {resource.overview}
              </p>
            </div>

            {/* Document Content Sections Rendered Safely */}
            <div 
              className="prose prose-slate dark:prose-invert max-w-none text-slate-700 dark:text-slate-350 text-xs sm:text-sm leading-relaxed space-y-4 
                prose-h3:text-sm prose-h3:font-bold prose-h3:font-display prose-h3:text-slate-850 dark:prose-h3:text-slate-200 prose-h3:mt-6 prose-h3:mb-2
                prose-p:mb-4 prose-p:leading-relaxed"
              dangerouslySetInnerHTML={{ __html: resource.content }}
            />

          </div>

          {/* Sidebar Navigation Context */}
          <div className="lg:col-span-4 space-y-6">
            
            {/* Table of Contents / Outline */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-3 transition-colors">
              <h3 className="text-xs font-bold font-display text-slate-400 dark:text-slate-550 uppercase tracking-wider">
                Document Outline
              </h3>
              <ul className="space-y-2">
                <li className="flex items-center gap-1 text-xs font-semibold text-primary-600 dark:text-primary-400">
                  <ChevronRight className="h-4 w-4 shrink-0" />
                  <span>Preliminary Definitions</span>
                </li>
                <li className="flex items-center gap-1 text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-primary-500 transition-colors cursor-pointer">
                  <ChevronRight className="h-4 w-4 shrink-0 opacity-0" />
                  <span>Establishment Procedures</span>
                </li>
                <li className="flex items-center gap-1 text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-primary-500 transition-colors cursor-pointer">
                  <ChevronRight className="h-4 w-4 shrink-0 opacity-0" />
                  <span>Membership Criteria</span>
                </li>
                <li className="flex items-center gap-1 text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-primary-500 transition-colors cursor-pointer">
                  <ChevronRight className="h-4 w-4 shrink-0 opacity-0" />
                  <span>Financial Management & Auditing</span>
                </li>
              </ul>
            </div>

            {/* Related Topics list */}
            {resource.relatedTopics && resource.relatedTopics.length > 0 && (
              <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-3 transition-colors">
                <h3 className="text-xs font-bold font-display text-slate-400 dark:text-slate-555 uppercase tracking-wider">
                  Related Topics
                </h3>
                <div className="flex flex-wrap gap-2">
                  {resource.relatedTopics.map((topic, idx) => (
                    <span 
                      key={idx} 
                      className="px-2.5 py-1 bg-slate-50 dark:bg-slate-950 border border-slate-200/50 dark:border-slate-850 text-[10px] font-semibold text-slate-600 dark:text-slate-400 rounded-lg"
                    >
                      {topic}
                    </span>
                  ))}
                </div>
              </div>
            )}

          </div>

        </div>

      </div>
    </LayoutWrapper>
  );
};
export default ResourceDetails;
