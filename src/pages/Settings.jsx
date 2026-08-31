import React, { useState } from 'react';
import { useLanguage, useTheme, useAccessibility, useAppData } from '../context/AppContext';
import { LayoutWrapper } from '../components/layout/LayoutWrapper';
import { Globe, Eye, MessageSquare, Shield, Trash2, CheckCircle2 } from 'lucide-react';

export const Settings = () => {
  const { t, language, setLanguage } = useLanguage();
  const { theme, setTheme } = useTheme();
  const { largerText, setLargerText, highContrast, setHighContrast } = useAccessibility();
  const { clearAllChatHistory, showToast } = useAppData();

  // Chat Preferences Local States
  const [showSources, setShowSources] = useState(true);
  const [saveHistory, setSaveHistory] = useState(true);
  const [voiceInput, setVoiceInput] = useState(false);

  const handleClearHistory = () => {
    if (window.confirm(t('clearHistoryConfirm'))) {
      clearAllChatHistory();
    }
  };

  const handleSavePref = (message) => {
    showToast(message, "success");
  };

  return (
    <LayoutWrapper title={t('settings')}>
      <div className="max-w-3xl mx-auto space-y-6 text-left animate-message-appear">
        
        {/* Title */}
        <div>
          <h2 className="text-xl font-bold font-display text-slate-800 dark:text-white">
            {t('settings')}
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Customize layout themes, multilingual settings, accessibility scales, and chat history parameters.
          </p>
        </div>

        {/* 1. Language settings card */}
        <section className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-5 sm:p-6 shadow-sm space-y-4 transition-colors">
          <h3 className="text-sm font-bold font-display text-slate-800 dark:text-white flex items-center gap-2.5">
            <Globe className="h-5 w-5 text-primary-600 dark:text-primary-400" />
            <span>{t('settingsLanguage')}</span>
          </h3>
          <p className="text-[11px] text-slate-400 dark:text-slate-500 leading-normal">
            Choose the language for the chatbot responses, search fields, and primary navigational links.
          </p>
          
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 max-w-lg pt-2">
            {[
              { code: 'en', name: 'English' },
              { code: 'kn', name: 'ಕನ್ನಡ' },
              { code: 'hi', name: 'हिन्दी' },
              { code: 'ne', name: 'नेपाली' }
            ].map((lang) => (
              <button
                key={lang.code}
                onClick={() => {
                  setLanguage(lang.code);
                  handleSavePref(`Language switched to ${lang.name}`);
                }}
                className={`py-2 rounded-xl text-xs font-semibold border transition-all cursor-pointer ${
                  language === lang.code
                    ? 'border-primary-500 bg-primary-50 text-primary-655 dark:bg-primary-950/20 dark:text-primary-400 font-bold'
                    : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 text-slate-600 hover:text-slate-800 dark:text-slate-350 dark:hover:text-white'
                }`}
              >
                {lang.name}
              </button>
            ))}
          </div>
        </section>

        {/* 2. Theme Card */}
        <section className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-5 sm:p-6 shadow-sm space-y-4 transition-colors">
          <h3 className="text-sm font-bold font-display text-slate-800 dark:text-white flex items-center gap-2.5">
            <Eye className="h-5 w-5 text-primary-600 dark:text-primary-400" />
            <span>{t('settingsAppearance')}</span>
          </h3>
          <p className="text-[11px] text-slate-400 dark:text-slate-500 leading-normal">
            Choose between clean light mode or high-readability slate dark mode theme presets.
          </p>
          
          <div className="grid grid-cols-3 gap-3 max-w-md pt-2">
            {[
              { id: 'light', name: t('themeLight') },
              { id: 'dark', name: t('themeDark') },
              { id: 'system', name: t('themeSystem') }
            ].map((themeOpt) => (
              <button
                key={themeOpt.id}
                onClick={() => {
                  setTheme(themeOpt.id);
                  handleSavePref(`Theme set to ${themeOpt.name}`);
                }}
                className={`py-2 rounded-xl text-xs font-semibold border transition-all cursor-pointer ${
                  theme === themeOpt.id
                    ? 'border-primary-500 bg-primary-50 text-primary-655 dark:bg-primary-950/20 dark:text-primary-400 font-bold'
                    : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 text-slate-600 hover:text-slate-800 dark:text-slate-350 dark:hover:text-white'
                }`}
              >
                {themeOpt.name}
              </button>
            ))}
          </div>
        </section>

        {/* 3. Accessibility preferences */}
        <section className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-5 sm:p-6 shadow-sm space-y-4 transition-colors">
          <h3 className="text-sm font-bold font-display text-slate-800 dark:text-white flex items-center gap-2.5">
            <Eye className="h-5 w-5 text-primary-600 dark:text-primary-400" />
            <span>{t('settingsAccessibility')}</span>
          </h3>
          
          <div className="space-y-4 pt-2">
            {/* Larger Text toggle */}
            <div className="flex items-center justify-between gap-4 p-3 bg-slate-50 dark:bg-slate-955 rounded-xl border border-slate-200/60 dark:border-slate-850">
              <div>
                <h4 className="text-xs font-bold text-slate-800 dark:text-slate-250 font-display">
                  {t('accLargerText')}
                </h4>
                <p className="text-[10px] text-slate-450 dark:text-slate-500 leading-normal mt-0.5">
                  Scales up content fonts to 18px base for easier reading of legal provisions.
                </p>
              </div>
              <input
                type="checkbox"
                checked={largerText}
                onChange={(e) => {
                  setLargerText(e.target.checked);
                  handleSavePref(e.target.checked ? "Large text enabled" : "Large text disabled");
                }}
                className="h-5 w-5 rounded border-slate-350 dark:border-slate-700 text-primary-600 focus:ring-primary-500 cursor-pointer"
              />
            </div>

            {/* High Contrast toggle */}
            <div className="flex items-center justify-between gap-4 p-3 bg-slate-50 dark:bg-slate-955 rounded-xl border border-slate-200/60 dark:border-slate-850">
              <div>
                <h4 className="text-xs font-bold text-slate-800 dark:text-slate-250 font-display">
                  {t('accHighContrast')}
                </h4>
                <p className="text-[10px] text-slate-450 dark:text-slate-500 leading-normal mt-0.5">
                  Enhances color bounds and increases contrast ratio to optimize visibility.
                </p>
              </div>
              <input
                type="checkbox"
                checked={highContrast}
                onChange={(e) => {
                  setHighContrast(e.target.checked);
                  handleSavePref(e.target.checked ? "High contrast enabled" : "High contrast disabled");
                }}
                className="h-5 w-5 rounded border-slate-350 dark:border-slate-700 text-primary-600 focus:ring-primary-500 cursor-pointer"
              />
            </div>
          </div>
        </section>

        {/* 4. Chat Preferences Card */}
        <section className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-5 sm:p-6 shadow-sm space-y-4 transition-colors">
          <h3 className="text-sm font-bold font-display text-slate-800 dark:text-white flex items-center gap-2.5">
            <MessageSquare className="h-5 w-5 text-primary-600 dark:text-primary-400" />
            <span>{t('settingsChatPreferences')}</span>
          </h3>

          <div className="space-y-3 pt-2">
            {[
              { id: 'sources', label: t('prefShowSources'), val: showSources, setter: setShowSources, desc: "Renders source act cards under AI answers." },
              { id: 'history', label: t('prefSaveHistory'), val: saveHistory, setter: setSaveHistory, desc: "Records logs of previous conversations." },
              { id: 'voice', label: t('prefEnableVoice'), val: voiceInput, setter: setVoiceInput, desc: "Enables vocal dictation using microphone hooks." }
            ].map((pref) => (
              <div key={pref.id} className="flex items-start justify-between gap-4 p-3 hover:bg-slate-50/50 dark:hover:bg-slate-950/20 rounded-xl transition-colors">
                <div>
                  <h4 className="text-xs font-semibold text-slate-750 dark:text-slate-300">
                    {pref.label}
                  </h4>
                  <p className="text-[10px] text-slate-450 dark:text-slate-500 leading-normal mt-0.5">
                    {pref.desc}
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={pref.val}
                  onChange={(e) => {
                    pref.setter(e.target.checked);
                    handleSavePref(`${pref.label} updated`);
                  }}
                  className="h-5.5 w-5.5 rounded border-slate-300 dark:border-slate-700 text-primary-600 focus:ring-primary-500 cursor-pointer shrink-0"
                />
              </div>
            ))}
          </div>
        </section>

        {/* 5. Privacy section */}
        <section className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-5 sm:p-6 shadow-sm space-y-4 transition-colors">
          <h3 className="text-sm font-bold font-display text-red-655 dark:text-red-400 flex items-center gap-2.5">
            <Shield className="h-5 w-5" />
            <span>{t('settingsPrivacy')}</span>
          </h3>

          <div className="space-y-4 pt-2">
            {/* Delete Chat History */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 border border-red-100 dark:border-red-950/30 bg-red-50/30 dark:bg-red-955/5 rounded-2xl">
              <div>
                <h4 className="text-xs font-bold text-slate-800 dark:text-slate-250 font-display">
                  {t('privClearHistory')}
                </h4>
                <p className="text-[10px] text-slate-500 dark:text-slate-400 leading-relaxed mt-1 max-w-md">
                  Permanently wipe all conversations from local memory cache. This action is irreversible.
                </p>
              </div>
              <button
                onClick={handleClearHistory}
                className="inline-flex items-center gap-1.5 px-4 py-2 border border-transparent rounded-lg text-xs font-bold text-white bg-red-600 hover:bg-red-700 shadow-sm transition-colors cursor-pointer shrink-0"
              >
                <Trash2 className="h-4 w-4" />
                <span>Wipe Chat Database</span>
              </button>
            </div>
          </div>
        </section>

      </div>
    </LayoutWrapper>
  );
};
export default Settings;
