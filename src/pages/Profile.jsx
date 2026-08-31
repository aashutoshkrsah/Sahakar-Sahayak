import React, { useState } from 'react';
import { useAuth, useLanguage, useAppData } from '../context/AppContext';
import { LayoutWrapper } from '../components/layout/LayoutWrapper';
import { User, Mail, Globe, Users, Save, HelpCircle } from 'lucide-react';

export const Profile = () => {
  const { user, isGuest, updateProfile } = useAuth();
  const { t } = useLanguage();
  const { showToast } = useAppData();

  const [name, setName] = useState(user?.name || "");
  const [email, setEmail] = useState(user?.email || "");
  const [prefLang, setPrefLang] = useState(user?.preferredLanguage || "en");
  const [userType, setUserType] = useState(user?.userType || "Citizen");
  const [isLoading, setIsLoading] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    if (isGuest) {
      showToast("Profile edits are disabled in Guest Mode.", "error");
      return;
    }

    setIsLoading(true);
    setTimeout(() => {
      updateProfile(name, email, prefLang, userType);
      showToast("Profile details updated successfully", "success");
      setIsLoading(false);
    }, 400);
  };

  return (
    <LayoutWrapper title={t('profile')}>
      <div className="max-w-2xl mx-auto space-y-6 text-left animate-message-appear">
        
        {/* Title */}
        <div>
          <h2 className="text-xl font-bold font-display text-slate-800 dark:text-white">
            {t('profile')}
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Manage your personal credentials, classification, and communication preferences.
          </p>
        </div>

        {/* Profile Editor Card */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-5 sm:p-8 shadow-sm transition-colors">
          {isGuest && (
            <div className="mb-6 p-4 bg-amber-50 dark:bg-amber-955/15 border border-amber-200 dark:border-amber-900/40 text-xs text-amber-850 dark:text-amber-300 rounded-2xl flex items-start gap-2.5 leading-normal">
              <HelpCircle className="h-5 w-5 text-amber-500 shrink-0" />
              <div>
                <span className="font-bold">Guest Mode Warning:</span> You are currently exploring as a guest. Profile modifications and settings changes will not persist. Create a profile to access full features.
              </div>
            </div>
          )}

          <form onSubmit={handleSave} className="space-y-6">
            
            {/* Display Initials Badge */}
            <div className="flex items-center gap-4">
              <div className="h-16 w-16 rounded-2xl bg-primary-100 dark:bg-primary-950 flex items-center justify-center text-primary-700 dark:text-primary-300 font-black font-display text-xl border border-primary-200 dark:border-primary-900/60 shadow-sm shrink-0">
                {name ? name.charAt(0) : "U"}
              </div>
              <div>
                <h3 className="text-base font-bold font-display text-slate-850 dark:text-white leading-none">
                  {name || "User Profile"}
                </h3>
                <p className="text-xs text-slate-450 dark:text-slate-500 mt-1.5 leading-none">
                  {isGuest ? "Temporary Guest" : userType}
                </p>
              </div>
            </div>

            {/* Inputs Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 pt-3">
              {/* Full Name */}
              <div className="space-y-1.5">
                <label className="block text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  {t('fullName')}
                </label>
                <div className="relative flex items-center">
                  <User className="absolute left-3.5 h-4.5 w-4.5 text-slate-400" />
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    disabled={isGuest}
                    className="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-205 dark:border-slate-800 rounded-xl text-slate-850 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 dark:focus:border-primary-400 text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
                  />
                </div>
              </div>

              {/* Email Address */}
              <div className="space-y-1.5">
                <label className="block text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  {t('emailAddress')}
                </label>
                <div className="relative flex items-center">
                  <Mail className="absolute left-3.5 h-4.5 w-4.5 text-slate-400" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    disabled={isGuest}
                    className="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-205 dark:border-slate-800 rounded-xl text-slate-855 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 dark:focus:border-primary-400 text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
                  />
                </div>
              </div>

              {/* Preferred Language selection */}
              <div className="space-y-1.5">
                <label className="block text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  {t('preferredLang')}
                </label>
                <div className="relative flex items-center">
                  <Globe className="absolute left-3.5 h-4.5 w-4.5 text-slate-400 pointer-events-none" />
                  <select
                    value={prefLang}
                    onChange={(e) => setPrefLang(e.target.value)}
                    disabled={isGuest}
                    className="w-full pl-10 pr-8 py-2.5 bg-slate-50 dark:bg-slate-955 border border-slate-205 dark:border-slate-800 rounded-xl text-slate-850 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 dark:focus:border-primary-400 text-sm transition-all appearance-none disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer shadow-sm"
                  >
                    <option value="en">English</option>
                    <option value="kn">ಕನ್ನಡ</option>
                    <option value="hi">हिन्दी</option>
                    <option value="ne">नेपाली</option>
                  </select>
                </div>
              </div>

              {/* User Type classification */}
              <div className="space-y-1.5">
                <label className="block text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  {t('userType')}
                </label>
                <div className="relative flex items-center">
                  <Users className="absolute left-3.5 h-4.5 w-4.5 text-slate-400 pointer-events-none" />
                  <select
                    value={userType}
                    onChange={(e) => setUserType(e.target.value)}
                    disabled={isGuest}
                    className="w-full pl-10 pr-8 py-2.5 bg-slate-50 dark:bg-slate-955 border border-slate-205 dark:border-slate-800 rounded-xl text-slate-850 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 dark:focus:border-primary-400 text-sm transition-all appearance-none disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer shadow-sm"
                  >
                    <option value="Citizen">{t('typeCitizen')}</option>
                    <option value="Cooperative Member">{t('typeMember')}</option>
                    <option value="Cooperative Manager">{t('typeManager')}</option>
                    <option value="Student / Researcher">{t('typeStudent')}</option>
                    <option value="Other">{t('typeOther')}</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Save Button */}
            {!isGuest && (
              <div className="pt-4 border-t border-slate-100 dark:border-slate-850 flex justify-end">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="inline-flex items-center gap-1.5 px-5 py-2.5 border border-transparent rounded-xl text-sm font-bold text-white bg-primary-600 hover:bg-primary-700 dark:bg-primary-600 dark:hover:bg-primary-700 shadow-md shadow-primary-500/10 hover:translate-y-[-1px] active:translate-y-0 transition-all cursor-pointer"
                >
                  <Save className="h-4.5 w-4.5" />
                  <span>{isLoading ? "Saving Changes..." : "Save Details"}</span>
                </button>
              </div>
            )}

          </form>

        </div>

      </div>
    </LayoutWrapper>
  );
};
export default Profile;
