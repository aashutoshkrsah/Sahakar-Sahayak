import React, { useState, useRef, useEffect } from 'react';
import { useLanguage } from '../../context/AppContext';
import { Globe, ChevronDown } from 'lucide-react';

export const LanguageSelector = ({ border = true, textClass = "text-sm font-medium" }) => {
  const { language, setLanguage } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'kn', name: 'ಕನ್ನಡ' },
    { code: 'hi', name: 'हिन्दी' },
    { code: 'ne', name: 'नेपाली' }
  ];

  const currentLang = languages.find(l => l.code === language) || languages[0];

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors select-none ${
          border ? 'border border-slate-200 dark:border-slate-700' : ''
        }`}
        aria-label="Select Language"
        aria-expanded={isOpen}
      >
        <Globe className="h-4.5 w-4.5 text-slate-400" />
        <span className={textClass}>{currentLang.name}</span>
        <ChevronDown className={`h-4 w-4 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <ul className="absolute right-0 mt-1.5 w-32 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg z-50 py-1 divide-y divide-slate-100 dark:divide-slate-700 animate-message-appear">
          {languages.map((lang) => (
            <li key={lang.code}>
              <button
                onClick={() => {
                  setLanguage(lang.code);
                  setIsOpen(false);
                }}
                className={`w-full text-left px-4 py-2 text-sm transition-colors hover:bg-primary-50 dark:hover:bg-primary-950/30 hover:text-primary-600 dark:hover:text-primary-400 ${
                  language === lang.code 
                    ? 'font-semibold text-primary-600 dark:text-primary-400 bg-primary-50/50 dark:bg-primary-950/20' 
                    : 'text-slate-600 dark:text-slate-300'
                }`}
              >
                {lang.name}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
export default LanguageSelector;
