import React from 'react';

export const Logo = ({ className = "h-8 w-8", withText = false, textClassName = "text-xl font-bold font-display" }) => {
  return (
    <div className="flex items-center gap-2 select-none">
      <svg 
        className={className} 
        viewBox="0 0 24 24" 
        fill="none" 
        xmlns="http://www.w3.org/2000/svg"
        aria-label="Sahakar Sahayak Logo"
      >
        {/* Outer Circular Cooperative Border */}
        <circle 
          cx="12" 
          cy="12" 
          r="10" 
          stroke="currentColor" 
          strokeWidth="2" 
          className="text-primary-600 dark:text-primary-400" 
        />
        {/* Governance Shield Structure */}
        <path 
          d="M12 5C14.5 5 17 6.5 17 6.5V11C17 14.5 13.5 17.5 12 18.5C10.5 17.5 7 14.5 7 11V6.5C7 6.5 9.5 5 12 5Z" 
          fill="currentColor" 
          fillOpacity="0.15" 
          stroke="currentColor" 
          strokeWidth="1.5" 
          className="text-primary-700 dark:text-primary-300" 
        />
        {/* Handshake/Trust Check Inner Marks */}
        <path 
          d="M9.5 11L11 12.5L14.5 9" 
          stroke="currentColor" 
          strokeWidth="2" 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          className="text-primary-600 dark:text-primary-400" 
        />
        {/* Hands/Community arches */}
        <path 
          d="M10 15.5C11 16 13 16 14 15.5" 
          stroke="currentColor" 
          strokeWidth="1.5" 
          strokeLinecap="round"
          className="text-primary-700 dark:text-primary-300"
        />
      </svg>
      {withText && (
        <span className={`${textClassName} text-slate-800 dark:text-slate-100 tracking-tight`}>
          Sahakar <span className="text-primary-600 dark:text-primary-400">Sahayak</span>
        </span>
      )}
    </div>
  );
};
