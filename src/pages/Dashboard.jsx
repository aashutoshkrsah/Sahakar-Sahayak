import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth, useLanguage, useAppData } from '../context/AppContext';
import { LayoutWrapper } from '../components/layout/LayoutWrapper';
import { QuickActionCard } from '../components/dashboard/QuickActionCard';
import { RecentQuestionRow } from '../components/dashboard/RecentQuestionRow';
import { 
  MessageSquare, 
  BookOpen, 
  Scale, 
  FileText, 
  Bookmark, 
  History, 
  Users, 
  ArrowRight,
  Search,
  FileCheck,
  Compass
} from 'lucide-react';

export const Dashboard = () => {
  const { user, isGuest } = useAuth();
  const { t } = useLanguage();
  const { chatHistory, savedAnswers } = useAppData();
  const navigate = useNavigate();

  const [searchQuery, setSearchQuery] = useState("");

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    // Launch search query in chat screen
    navigate('/chat', { state: { initialQuery: searchQuery } });
  };

  // Stat Indicators
  const stats = [
    { label: t('statRecentConversations'), value: isGuest ? 0 : chatHistory.length, icon: History, color: 'text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/20' },
    { label: t('statSavedAnswers'), value: isGuest ? 0 : savedAnswers.length, icon: Bookmark, color: 'text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/20' },
    { label: t('statDocuments'), value: 6, icon: FileText, color: 'text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/20' },
    { label: t('statResourcesExplored'), value: 5, icon: Scale, color: 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/20' }
  ];

  // Quick Action grid cards
  const quickActions = [
    { title: t('qaAskSahayak'), description: "Ask cooperative questions in natural language.", icon: MessageSquare, to: "/chat" },
    { title: t('qaExploreLaws'), description: "Browse and search cooperative acts and regulations.", icon: Scale, to: "/resources" },
    { title: t('qaCheckDocs'), description: "See checklist documents required for registration and audits.", icon: FileText, to: "/documents" },
    { title: t('qaUnderstandRights'), description: "Understand voting guidelines and member responsibilities.", icon: Users, to: "/guide" },
    { title: t('qaViewSaved'), description: "Access bookmarked answers offline.", icon: Bookmark, to: "/saved", disabledForGuest: true },
    { title: t('qaContinueChat'), description: "Resume your most recent query.", icon: History, to: isGuest ? "/chat" : "/history", disabledForGuest: true }
  ];

  // Filter latest questions from history state
  const latestQuestions = isGuest 
    ? [] 
    : chatHistory.slice(0, 3).map(chat => {
        const lastUserMessage = [...chat.messages].reverse().find(m => m.sender === 'user');
        return {
          id: chat.id,
          question: lastUserMessage ? lastUserMessage.text : chat.title,
          category: chat.category,
          date: chat.date
        };
      });

  return (
    <LayoutWrapper title={t('dashboard')}>
      {/* Header welcome banner */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 dark:from-primary-700 dark:to-primary-850 rounded-3xl p-6 sm:p-8 text-white relative overflow-hidden shadow-lg shadow-primary-600/10 transition-colors">
        <div className="absolute right-0 top-0 bottom-0 opacity-10 flex items-center pointer-events-none">
          <BookOpen className="h-64 w-64 translate-x-20" />
        </div>

        <div className="relative z-10 space-y-4">
          <div className="space-y-1">
            <h2 className="text-2xl sm:text-3xl font-black font-display tracking-tight leading-none">
              {t('welcomeBack')}, {user ? user.name : "Guest"} 👋
            </h2>
            <p className="text-sm font-medium opacity-90 leading-normal">
              {t('howCanIHelp')}
            </p>
          </div>

          {/* Search Box */}
          <form onSubmit={handleSearchSubmit} className="flex items-center bg-white dark:bg-slate-900 rounded-2xl p-1.5 shadow-md w-full max-w-2xl text-slate-800 dark:text-slate-100">
            <Search className="h-5 w-5 text-slate-400 ml-3.5 shrink-0" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={t('searchQuestionPlaceholder')}
              className="w-full bg-transparent px-3 py-2 text-sm border-0 focus:outline-none focus:ring-0 text-slate-850 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500"
            />
            <button
              type="submit"
              className="px-5 py-2 border border-transparent rounded-xl text-sm font-bold text-white bg-primary-600 hover:bg-primary-700 dark:bg-primary-600 dark:hover:bg-primary-700 shadow-sm transition-colors cursor-pointer shrink-0"
            >
              Ask
            </button>
          </form>
        </div>
      </div>

      {/* Stats Indicators Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, idx) => {
          const Icon = stat.icon;
          return (
            <div key={idx} className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 rounded-2xl p-4 flex items-center justify-between shadow-sm transition-colors">
              <div className="space-y-1">
                <span className="text-[10px] sm:text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider block">
                  {stat.label}
                </span>
                <span className="text-xl sm:text-2xl font-extrabold font-display text-slate-855 dark:text-white leading-none block">
                  {stat.value}
                </span>
              </div>
              <div className={`p-2.5 rounded-xl ${stat.color} shrink-0`}>
                <Icon className="h-5 w-5" />
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Grid: Quick Actions & Recent Questions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Side: Quick Actions Grid */}
        <div className="lg:col-span-2 space-y-4 text-left">
          <h3 className="text-base font-bold font-display text-slate-800 dark:text-white">
            {t('quickActions')}
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {quickActions.map((action, idx) => {
              const Icon = action.icon;
              const isDisabled = isGuest && action.disabledForGuest;
              
              if (isDisabled) return null; // Hide guest-restricted quick actions on guest login

              return (
                <QuickActionCard
                  key={idx}
                  title={action.title}
                  description={action.description}
                  icon={Icon}
                  to={action.to}
                />
              );
            })}
          </div>
        </div>

        {/* Right Side: Recent Questions list */}
        <div className="space-y-4 text-left">
          <div className="flex justify-between items-center">
            <h3 className="text-base font-bold font-display text-slate-800 dark:text-white">
              {t('recentQuestions')}
            </h3>
            {!isGuest && chatHistory.length > 0 && (
              <button 
                onClick={() => navigate('/history')}
                className="text-[11px] font-bold text-primary-600 hover:text-primary-750 dark:text-primary-400 hover:underline inline-flex items-center gap-0.5"
              >
                <span>View All</span>
                <ArrowRight className="h-3 w-3" />
              </button>
            )}
          </div>

          <div className="space-y-3">
            {isGuest ? (
              <div className="p-6 bg-slate-50/50 dark:bg-slate-900/50 border border-slate-200/50 dark:border-slate-800 border-dashed rounded-2xl text-center space-y-2">
                <Compass className="h-8 w-8 text-slate-400 mx-auto" />
                <h4 className="text-xs font-semibold text-slate-700 dark:text-slate-350">Guest Mode Active</h4>
                <p className="text-[10px] text-slate-500 max-w-[200px] mx-auto leading-normal">
                  Create a profile to save answers and track your ongoing conversation threads.
                </p>
                <button
                  onClick={() => navigate('/register')}
                  className="mt-2 text-[10px] font-bold text-white bg-primary-600 px-3 py-1.5 rounded-lg hover:bg-primary-700 transition-colors"
                >
                  Register Now
                </button>
              </div>
            ) : latestQuestions.length === 0 ? (
              <div className="p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl text-center space-y-2.5 shadow-sm">
                <MessageSquare className="h-8 w-8 text-slate-400 mx-auto" />
                <p className="text-xs font-medium text-slate-500 dark:text-slate-400 leading-normal max-w-[160px] mx-auto">
                  {t('emptyHistory')}
                </p>
                <button
                  onClick={() => navigate('/chat')}
                  className="text-xs font-bold text-primary-600 hover:underline inline-flex items-center gap-0.5"
                >
                  <span>{t('askFirstQuestion')}</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </button>
              </div>
            ) : (
              latestQuestions.map((row) => (
                <RecentQuestionRow
                  key={row.id}
                  chatId={row.id}
                  question={row.question}
                  category={row.category}
                  date={row.date}
                />
              ))
            )}
          </div>
        </div>

      </div>
    </LayoutWrapper>
  );
};
export default Dashboard;
