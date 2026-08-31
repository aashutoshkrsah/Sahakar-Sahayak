import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

export const QuickActionCard = ({ title, description, icon: Icon, to, onClick }) => {
  const navigate = useNavigate();

  const handlePress = () => {
    if (onClick) {
      onClick();
    } else if (to) {
      navigate(to);
    }
  };

  return (
    <button
      onClick={handlePress}
      className="flex flex-col text-left p-5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl transition-all duration-200 hover:shadow-md hover:border-primary-200 dark:hover:border-primary-900/50 hover:translate-y-[-1px] group w-full"
    >
      <div className="h-10 w-10 rounded-xl bg-primary-50 dark:bg-primary-950/40 flex items-center justify-center text-primary-600 dark:text-primary-400 mb-4 group-hover:scale-105 transition-transform">
        {Icon && <Icon className="h-5 w-5" />}
      </div>
      <h3 className="text-sm font-bold font-display text-slate-850 dark:text-white mb-1.5 leading-snug">
        {title}
      </h3>
      <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed mb-4 flex-1">
        {description}
      </p>
      <div className="flex items-center gap-1 text-xs font-bold text-primary-600 dark:text-primary-400 group-hover:gap-1.5 transition-all">
        <span>Go</span>
        <ArrowRight className="h-3.5 w-3.5" />
      </div>
    </button>
  );
};
export default QuickActionCard;
