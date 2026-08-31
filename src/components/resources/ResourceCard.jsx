import React from 'react';
import { Link } from 'react-router-dom';
import { Calendar, FileText, ArrowRight } from 'lucide-react';
import { useLanguage } from '../../context/AppContext';

export const ResourceCard = ({ id, title, description, category, lastUpdated }) => {
  const { t } = useLanguage();

  const getCategoryColor = (cat) => {
    switch (cat.toLowerCase()) {
      case 'laws':
        return 'bg-blue-50 text-blue-700 border-blue-150 dark:bg-blue-950/20 dark:text-blue-400 dark:border-blue-900/40';
      case 'regulations':
        return 'bg-purple-50 text-purple-700 border-purple-150 dark:bg-purple-950/20 dark:text-purple-400 dark:border-purple-900/40';
      case 'guidelines':
        return 'bg-amber-50 text-amber-700 border-amber-150 dark:bg-amber-950/20 dark:text-amber-400 dark:border-amber-900/40';
      case 'policies':
        return 'bg-emerald-50 text-emerald-700 border-emerald-150 dark:bg-emerald-950/20 dark:text-emerald-400 dark:border-emerald-900/40';
      default:
        return 'bg-slate-50 text-slate-700 border-slate-150 dark:bg-slate-900 dark:text-slate-400 dark:border-slate-800';
    }
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl p-5 hover:shadow-md hover:border-slate-300 dark:hover:border-slate-700 transition-all flex flex-col justify-between group">
      <div className="space-y-3">
        {/* Category & Date */}
        <div className="flex items-center justify-between gap-2">
          <span className={`text-[10px] font-bold px-2 py-0.5 border rounded-full uppercase tracking-wider ${getCategoryColor(category)}`}>
            {category}
          </span>
          <span className="flex items-center gap-1.5 text-[10px] text-slate-400 dark:text-slate-500">
            <Calendar className="h-3.5 w-3.5" />
            {lastUpdated}
          </span>
        </div>

        {/* Title */}
        <h3 className="text-sm font-bold font-display text-slate-800 dark:text-white leading-snug group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
          {title}
        </h3>

        {/* Description */}
        <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed line-clamp-2">
          {description}
        </p>
      </div>

      {/* Footer Link */}
      <div className="mt-5 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
        <span className="flex items-center gap-1.5 text-[10px] font-semibold text-slate-450 dark:text-slate-500">
          <FileText className="h-3.5 w-3.5" />
          Acts & Rules Document
        </span>
        <Link
          to={`/resources/${id}`}
          className="inline-flex items-center gap-1 text-xs font-bold text-primary-600 dark:text-primary-400 group-hover:gap-1.5 transition-all"
        >
          <span>{t('viewDetails')}</span>
          <ArrowRight className="h-3.5 w-3.5" />
        </Link>
      </div>
    </div>
  );
};
export default ResourceCard;
