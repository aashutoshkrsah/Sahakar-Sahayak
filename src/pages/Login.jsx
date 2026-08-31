import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth, useLanguage } from '../context/AppContext';
import { Logo } from '../components/common/Logo';
import { ArrowRight, Mail, Lock, LogIn, UserCheck } from 'lucide-react';

export const Login = () => {
  const { login, continueAsGuest } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!email || !password) {
      setError("Please fill in all fields.");
      return;
    }

    setIsLoading(true);
    try {
      // Mock login validation
      login(email, password, "Sita Ram", "Citizen");
      navigate('/dashboard');
    } catch (err) {
      setError("Invalid credentials. Try guest mode.");
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
          Sign in to Sahakar Sahayak
        </h2>
        <p className="mt-1 text-center text-xs text-slate-400 dark:text-slate-550">
          “Cooperative knowledge and legal guidance, made simple.”
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
        <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 py-8 px-6 sm:px-10 rounded-2xl shadow-sm transition-colors">
          
          {error && (
            <div className="mb-4 p-3 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/40 text-xs font-semibold text-red-600 dark:text-red-400 rounded-lg animate-message-appear">
              {error}
            </div>
          )}

          <form className="space-y-5" onSubmit={handleSubmit}>
            {/* Email Input */}
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

            {/* Password Input */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center">
                <label htmlFor="password" className="block text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  {t('password')}
                </label>
                <a href="#forgot" className="text-[10px] font-bold text-primary-600 hover:text-primary-700 dark:text-primary-400">
                  {t('forgotPassword')}
                </a>
              </div>
              <div className="relative flex items-center">
                <Lock className="absolute left-3 h-4 w-4 text-slate-400" />
                <input
                  id="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-9.5 pr-4 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-slate-800 dark:text-slate-100 placeholder-slate-450 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 dark:focus:border-primary-400 text-sm transition-all"
                />
              </div>
            </div>

            {/* Remember Me */}
            <div className="flex items-center">
              <input
                id="remember-me"
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="h-4 w-4 rounded border-slate-350 dark:border-slate-700 text-primary-600 focus:ring-primary-500"
              />
              <label htmlFor="remember-me" className="ml-2 block text-xs font-semibold text-slate-650 dark:text-slate-400">
                {t('rememberMe')}
              </label>
            </div>

            {/* Log In Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full inline-flex items-center justify-center gap-2 py-2.5 border border-transparent rounded-lg text-sm font-bold text-white bg-primary-600 hover:bg-primary-700 dark:bg-primary-600 dark:hover:bg-primary-700 shadow-md shadow-primary-500/10 hover:translate-y-[-1px] active:translate-y-[0] transition-all cursor-pointer"
            >
              <LogIn className="h-4.5 w-4.5" />
              <span>{isLoading ? "Signing in..." : t('login')}</span>
            </button>
          </form>

          {/* Spacer / Separator */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200 dark:border-slate-800" />
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="bg-white dark:bg-slate-900 px-3 text-slate-400 dark:text-slate-500">
                Or explore without password
              </span>
            </div>
          </div>

          {/* Guest CTA */}
          <button
            onClick={handleGuestLogin}
            className="w-full inline-flex items-center justify-center gap-2 py-2.5 border border-slate-200 dark:border-slate-800 rounded-lg text-sm font-bold text-slate-700 dark:text-slate-200 bg-slate-50 hover:bg-slate-100 dark:bg-slate-800 dark:hover:bg-slate-800/80 transition-colors cursor-pointer"
          >
            <UserCheck className="h-4.5 w-4.5 text-slate-400" />
            <span>{t('continueAsGuest')}</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </button>

          {/* Register Link */}
          <div className="text-center mt-6">
            <Link to="/register" className="text-xs font-bold text-primary-655 hover:text-primary-700 dark:text-primary-400">
              {t('dontHaveAccount')}
            </Link>
          </div>

        </div>
      </div>
    </div>
  );
};
export default Login;
