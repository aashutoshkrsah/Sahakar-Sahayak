import React from 'react';

export const FeatureCard = ({ title, description, icon: Icon }) => {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl p-6 transition-all duration-300 hover:shadow-lg hover:shadow-primary-500/5 hover:translate-y-[-2px] group">
      <div className="h-12 w-12 rounded-xl bg-primary-50 dark:bg-primary-950/40 flex items-center justify-center text-primary-600 dark:text-primary-400 mb-5 group-hover:scale-110 transition-transform duration-300">
        {Icon && <Icon className="h-6 w-6" />}
      </div>
      <h3 className="text-base font-bold font-display text-slate-800 dark:text-white mb-2 leading-snug">
        {title}
      </h3>
      <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
        {description}
      </p>
    </div>
  );
};
export default FeatureCard;
