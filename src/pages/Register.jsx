import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth, useLanguage } from '../context/AppContext';
import { Logo } from '../components/common/Logo';
import { ArrowRight, User, Mail, Lock, UserPlus, Globe, HelpCircle } from 'lucide-react';

export const Register = () => {
  const { register, continueAsGuest } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [userType, setUserType] = useState("Citizen");
  const [preferredLanguage, setPreferredLanguage] = useState("en");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!name || !email || !password || !confirmPassword) {
      setError("Please fill in all fields.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setIsLoading(true);
    try {
      // Mock registration
      register(name, email, password, userType);
      navigate('/dashboard');
    } catch (err) {
      setError("Failed to register. Try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleGuestLogin = () => {
    continueAsGuest();
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8 transition-colors duration-150">
      <div className="sm:mx-auto sm:w-full sm:max-w-md flex flex-col items-center">
        <Link to="/">
          <Logo className="h-12 w-12" />
        </Link>
        <h2 className="mt-6 text-center text-2xl font-black font-display text-slate-850 dark:text-white">
          Create your account
        </h2>
        <p className="mt-1 text-center text-xs text-slate-400 dark:text-slate-550">
          Unlock personalized dashboards and save custom legal answers.
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
        <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 py-8 px-6 sm:px-10 rounded-2xl shadow-sm transition-colors">
          
          {error && (
            <div className="mb-4 p-3 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/40 text-xs font-semibold text-red-600 dark:text-red-400 rounded-lg animate-message-appear">
              {error}
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit}>
            {/* Full Name */}
            <div className="space-y-1.5">
              <label htmlFor="name" className="block text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                {t('fullName')}
              </label>
              <div className="relative flex items-center">
                <User className="absolute left-3 h-4 w-4 text-slate-400" />
                <input
                  id="name"
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Sita Ram"
                  className="w-full pl-9.5 pr-4 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-slate-800 dark:text-slate-100 placeholder-slate-450 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 dark:focus:border-primary-400 text-sm transition-all"
                />
              </div>
            </div>

            {/* Email */}
            <div className="space-y-1.5">
              <label htmlFor="email" className="block text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                {t('emailAddress')}
              </label>
              <div className="relative flex items-center">
                <Mail className="absolute left-3 h-4 w-4 text-slate-400" />
                <input
                  id="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.gov.np"
                  className="w-full pl-9.5 pr-4 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-slate-800 dark:text-slate-100 placeholder-slate-450 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 dark:focus:border-primary-400 text-sm transition-all"
                />
              </div>
            </div>

            {/* Language & User Type Row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Preferred Language */}
              <div className="space-y-1.5">
                <label htmlFor="language" className="block text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  {t('preferredLang')}
                </label>
                <div className="relative flex items-center">
                  <Globe className="absolute left-3 h-4 w-4 text-slate-400 pointer-events-none" />
                  <select
                    id="language"
                    value={preferredLanguage}
                    onChange={(e) => setPreferredLanguage(e.target.value)}
                    className="w-full pl-9.5 pr-8 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 dark:focus:border-primary-400 text-sm transition-all appearance-none cursor-pointer"
                  >
                    <option value="en">English</option>
                    <option value="kn">ಕನ್ನಡ</option>
                    <option value="hi">हिन्दी</option>
                    <option value="ne">नेपाली</option>
                  </select>
                </div>
              </div>

              {/* User Type */}
              <div className="space-y-1.5">
                <label htmlFor="user-type" className="block text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  {t('userType')}
                </label>
                <div className="relative flex items-center">
                  <HelpCircle className="absolute left-3 h-4 w-4 text-slate-400 pointer-events-none" />
                  <select
                    id="user-type"
                    value={userType}
                    onChange={(e) => setUserType(e.target.value)}
                    className="w-full pl-9.5 pr-8 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 dark:focus:border-primary-400 text-sm transition-all appearance-none cursor-pointer"
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

            {/* Passwords */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Password */}
              <div className="space-y-1.5">
                <label htmlFor="register-password" className="block text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  {t('password')}
                </label>
                <div className="relative flex items-center">
                  <Lock className="absolute left-3 h-4 w-4 text-slate-400" />
                  <input
                    id="register-password"
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-9.5 pr-4 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-slate-800 dark:text-slate-100 placeholder-slate-450 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 dark:focus:border-primary-400 text-sm transition-all"
                  />
                </div>
              </div>

              {/* Confirm Password */}
              <div className="space-y-1.5">
                <label htmlFor="confirm-password" className="block text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  Confirm Password
                </label>
                <div className="relative flex items-center">
                  <Lock className="absolute left-3 h-4 w-4 text-slate-400" />
                  <input
                    id="confirm-password"
                    type="password"
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-9.5 pr-4 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-slate-800 dark:text-slate-100 placeholder-slate-450 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 dark:focus:border-primary-400 text-sm transition-all"
                  />
                </div>
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full inline-flex items-center justify-center gap-2 py-2.5 border border-transparent rounded-lg text-sm font-bold text-white bg-primary-600 hover:bg-primary-700 dark:bg-primary-600 dark:hover:bg-primary-700 shadow-md shadow-primary-500/10 hover:translate-y-[-1px] active:translate-y-[0] transition-all cursor-pointer"
            >
              <UserPlus className="h-4.5 w-4.5" />
              <span>{isLoading ? "Creating..." : t('register')}</span>
            </button>
          </form>

          {/* Spacer */}
          <div className="relative my-5">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200 dark:border-slate-800" />
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="bg-white dark:bg-slate-900 px-3 text-slate-400 dark:text-slate-500">
                Or bypass credentials
              </span>
            </div>
          </div>

          {/* Guest Action */}
          <button
            onClick={handleGuestLogin}
            className="w-full inline-flex items-center justify-center gap-2 py-2.5 border border-slate-200 dark:border-slate-800 rounded-lg text-sm font-bold text-slate-700 dark:text-slate-200 bg-slate-50 hover:bg-slate-100 dark:bg-slate-800 dark:hover:bg-slate-800/80 transition-colors cursor-pointer"
          >
            <span>{t('continueAsGuest')}</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </button>

          {/* Login Link */}
          <div className="text-center mt-5">
            <Link to="/login" className="text-xs font-bold text-primary-655 hover:text-primary-700 dark:text-primary-400">
              {t('alreadyHaveAccount')}
            </Link>
          </div>

        </div>
      </div>
    </div>
  );
};
export default Register;
