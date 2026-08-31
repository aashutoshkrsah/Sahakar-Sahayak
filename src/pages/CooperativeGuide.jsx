import React, { useState } from 'react';
import { useLanguage } from '../context/AppContext';
import { LayoutWrapper } from '../components/layout/LayoutWrapper';
import { CategoryCard } from '../components/resources/CategoryCard';
import { SearchBar } from '../components/common/SearchBar';
import { cooperativeGuideCategories } from '../data/mockData';
import { ArrowLeft, BookOpen, ChevronRight, HelpCircle, MessageSquare } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const CooperativeGuide = () => {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [selectedCategoryId, setSelectedCategoryId] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");

  const handleCategoryClick = (catId) => {
    setSelectedCategoryId(catId);
    setSearchQuery("");
  };

  const handleBackToCategories = () => {
    setSelectedCategoryId(null);
    setSearchQuery("");
  };

  const handleAskAboutArticle = (articleTitle) => {
    navigate('/chat', { state: { initialQuery: `Ask me anything about: ${articleTitle}`, initialCategory: 'Guide' } });
  };

  // Filter categories based on search input (if on category overview screen)
  const filteredCategories = cooperativeGuideCategories.filter(cat => {
    if (!searchQuery) return true;
    const lowerQuery = searchQuery.toLowerCase();
    return (
      cat.title.toLowerCase().includes(lowerQuery) ||
      cat.description.toLowerCase().includes(lowerQuery) ||
      cat.articles.some(art => 
        art.title.toLowerCase().includes(lowerQuery) || 
        art.content.toLowerCase().includes(lowerQuery)
      )
    );
  });

  const selectedCategory = cooperativeGuideCategories.find(c => c.id === selectedCategoryId);

  // Filter articles inside a selected category
  const filteredArticles = selectedCategory 
    ? selectedCategory.articles.filter(art => {
        if (!searchQuery) return true;
        const lowerQuery = searchQuery.toLowerCase();
        return (
          art.title.toLowerCase().includes(lowerQuery) ||
          art.content.toLowerCase().includes(lowerQuery)
        );
      })
    : [];

  return (
    <LayoutWrapper title={t('cooperativeGuide')}>
      <div className="space-y-6 text-left">
        
        {/* Header Title Section */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h2 className="text-xl font-bold font-display text-slate-800 dark:text-white">
              {selectedCategory ? selectedCategory.title : t('cooperativeGuide')}
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-xl leading-relaxed">
              {selectedCategory ? selectedCategory.description : t('guideDescription')}
            </p>
          </div>
          
          {selectedCategory && (
            <button
              onClick={handleBackToCategories}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 border border-slate-200 dark:border-slate-850 bg-white dark:bg-slate-900 rounded-lg text-xs font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back to Categories</span>
            </button>
          )}
        </div>

        {/* Global Search Bar */}
        <SearchBar
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onClear={() => setSearchQuery("")}
          placeholder={selectedCategory ? `Search articles in ${selectedCategory.title}...` : t('guideSearchPlaceholder')}
        />

        {/* Dynamic Display Layout */}
        {!selectedCategory ? (
          /* 1. Category Overview List */
          filteredCategories.length === 0 ? (
            <div className="p-12 text-center bg-white dark:bg-slate-900 border border-slate-200/50 dark:border-slate-850 rounded-2xl">
              <HelpCircle className="h-10 w-10 text-slate-400 mx-auto mb-3" />
              <p className="text-sm font-semibold text-slate-700 dark:text-slate-350">{t('noResultsFound')}</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {filteredCategories.map((cat) => (
                <CategoryCard
                  key={cat.id}
                  id={cat.id}
                  title={cat.title}
                  description={cat.description}
                  iconName={cat.icon}
                  articleCount={cat.articles.length}
                  onClick={handleCategoryClick}
                />
              ))}
            </div>
          )
        ) : (
          /* 2. Detailed Articles Accordion / Article List View */
          filteredArticles.length === 0 ? (
            <div className="p-12 text-center bg-white dark:bg-slate-900 border border-slate-200/50 dark:border-slate-855 rounded-2xl">
              <HelpCircle className="h-10 w-10 text-slate-400 mx-auto mb-3" />
              <p className="text-sm font-semibold text-slate-700 dark:text-slate-350">{t('noResultsFound')}</p>
              <button 
                onClick={() => setSearchQuery("")} 
                className="mt-2 text-xs text-primary-600 font-bold hover:underline"
              >
                Clear Search Query
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {filteredArticles.map((art) => (
                <article 
                  key={art.id}
                  className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 rounded-2xl p-5 sm:p-6 shadow-sm space-y-4 transition-colors"
                >
                  <div className="flex justify-between items-start gap-4">
                    <h3 className="text-base font-bold font-display text-slate-850 dark:text-white leading-snug">
                      {art.title}
                    </h3>
                    <button
                      onClick={() => handleAskAboutArticle(art.title)}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-primary-50 hover:bg-primary-100 dark:bg-primary-950/20 dark:hover:bg-primary-950/40 text-primary-700 dark:text-primary-400 rounded-lg text-[10px] font-bold transition-colors"
                      title="Ask Sahayak About This Article"
                    >
                      <MessageSquare className="h-3.5 w-3.5" />
                      <span>Ask Sahayak</span>
                    </button>
                  </div>
                  
                  <p className="text-xs text-slate-650 dark:text-slate-350 leading-relaxed whitespace-pre-line">
                    {art.content}
                  </p>

                  {/* Subsections rendering */}
                  {art.sections && art.sections.length > 0 && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 pt-4 border-t border-slate-100 dark:border-slate-850">
                      {art.sections.map((section, sIdx) => (
                        <div key={sIdx} className="space-y-1.5 p-3.5 bg-slate-50 dark:bg-slate-950 border border-slate-200/40 dark:border-slate-850 rounded-xl">
                          <h4 className="text-xs font-bold text-slate-800 dark:text-slate-250 font-display">
                            {section.subtitle}
                          </h4>
                          <p className="text-[11px] text-slate-500 dark:text-slate-405 leading-relaxed whitespace-pre-wrap">
                            {section.text}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </article>
              ))}
            </div>
          )
        )}
        
      </div>
    </LayoutWrapper>
  );
};
export default CooperativeGuide;
