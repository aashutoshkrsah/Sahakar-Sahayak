import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/AppContext';
import { LayoutWrapper } from '../components/layout/LayoutWrapper';
import { ResourceCard } from '../components/resources/ResourceCard';
import { SearchBar } from '../components/common/SearchBar';
import { resourceService } from '../services/resourceService';
import { Scale, HelpCircle } from 'lucide-react';

export const LegalResources = () => {
  const { t } = useLanguage();
  const [searchQuery, setSearchQuery] = useState("");
  const [activeCategory, setActiveCategory] = useState("All");
  const [resources, setResources] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const categories = ["All", "Laws", "Regulations", "Guidelines", "Policies"];

  useEffect(() => {
    const fetchResources = async () => {
      setIsLoading(true);
      try {
        const data = await resourceService.searchResources(searchQuery, activeCategory);
        setResources(data);
      } catch (err) {
        console.error("Failed to load legal resources:", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchResources();
  }, [searchQuery, activeCategory]);

  return (
    <LayoutWrapper title={t('legalResources')}>
      <div className="space-y-6 text-left">
        
        {/* Title */}
        <div>
          <h2 className="text-xl font-bold font-display text-slate-800 dark:text-white">
            {t('legalResources')}
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            {t('legalDescription')}
          </p>
        </div>

        {/* Search Input */}
        <SearchBar
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onClear={() => setSearchQuery("")}
          placeholder={t('legalSearchPlaceholder')}
        />

        {/* Tab Filters */}
        <div className="flex flex-wrap gap-2 pb-2 border-b border-slate-200/50 dark:border-slate-850">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`px-4 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                activeCategory === cat
                  ? 'bg-primary-600 text-white shadow-sm'
                  : 'bg-white dark:bg-slate-900 border border-slate-250 dark:border-slate-800 text-slate-600 hover:text-slate-850 dark:text-slate-350 dark:hover:text-white'
              }`}
            >
              {cat === "All" ? t('categoryAll') : t(`category${cat}`)}
            </button>
          ))}
        </div>

        {/* Resource Cards Grid */}
        {isLoading ? (
          <div className="py-12 text-center text-slate-500">
            <span className="inline-block h-6 w-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></span>
            <p className="text-xs font-semibold mt-2">Loading official archives...</p>
          </div>
        ) : resources.length === 0 ? (
          <div className="p-12 text-center bg-white dark:bg-slate-900 border border-slate-200/50 dark:border-slate-850 rounded-2xl">
            <HelpCircle className="h-10 w-10 text-slate-400 mx-auto mb-3" />
            <p className="text-sm font-semibold text-slate-700 dark:text-slate-350">{t('noResultsFound')}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {resources.map((res) => (
              <ResourceCard
                key={res.id}
                id={res.id}
                title={res.title}
                description={res.description}
                category={res.category}
                lastUpdated={res.lastUpdated}
              />
            ))}
          </div>
        )}

      </div>
    </LayoutWrapper>
  );
};
export default LegalResources;
