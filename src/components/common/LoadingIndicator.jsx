import React from 'react';

export const LoadingIndicator = ({ text = "Loading..." }) => {
  return (
    <div className="flex flex-col items-center justify-center p-6 gap-3 text-center">
      <div className="flex items-center gap-1.5 justify-center py-2">
        <span className="h-2.5 w-2.5 rounded-full bg-primary-600 dark:bg-primary-400 animate-bounce-slow-1"></span>
        <span className="h-2.5 w-2.5 rounded-full bg-primary-600 dark:bg-primary-400 animate-bounce-slow-2"></span>
        <span className="h-2.5 w-2.5 rounded-full bg-primary-600 dark:bg-primary-400 animate-bounce-slow-3"></span>
      </div>
      <p className="text-xs font-medium text-slate-500 dark:text-slate-400 animate-pulse-subtle">
        {text}
      </p>
    </div>
  );
};
export default LoadingIndicator;
