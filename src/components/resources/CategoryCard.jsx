import React from 'react';
import * as Icons from 'lucide-react';
import { ArrowRight } from 'lucide-react';

export const CategoryCard = ({ id, title, description, iconName, articleCount, onClick }) => {
  // Resolve icon dynamically from Lucide
  const Icon = Icons[iconName] || Icons.BookOpen;

  return (
    <button
      onClick={() => onClick(id)}
      className="flex flex-col text-left p-5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl hover:shadow-md hover:border-primary-200 dark:hover:border-primary-900/50 hover:translate-y-[-1px] transition-all group w-full"
    >
      <div className="flex justify-between items-start w-full mb-4">
        <div className="h-10 w-10 rounded-xl bg-primary-50 dark:bg-primary-950/40 flex items-center justify-center text-primary-600 dark:text-primary-400 group-hover:scale-105 transition-transform">
          <Icon className="h-5 w-5" />
        </div>
        <span className="text-[10px] bg-slate-100 dark:bg-slate-850 text-slate-500 dark:text-slate-400 px-2 py-0.5 rounded-full font-semibold">
          {articleCount} {articleCount === 1 ? 'Article' : 'Articles'}
        </span>
      </div>

      <h3 className="text-sm font-bold font-display text-slate-850 dark:text-white mb-1.5 leading-snug group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
        {title}
      </h3>
      <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed mb-4 flex-1">
        {description}
      </p>

      <div className="flex items-center gap-1 text-xs font-bold text-primary-600 dark:text-primary-400 group-hover:gap-1.5 transition-all mt-auto">
        <span>Explore Guide</span>
        <ArrowRight className="h-3.5 w-3.5" />
      </div>
    </button>
  );
};
export default CategoryCard;
