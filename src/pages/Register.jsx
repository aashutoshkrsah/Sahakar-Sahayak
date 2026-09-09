import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth, useLanguage, useAppData } from '../context/AppContext';
import { Logo } from '../components/common/Logo';
import { authService } from '../services/authService';
import { 
  ArrowRight, 
  User, 
  Mail, 
  Phone, 
  Lock, 
  UserPlus, 
  Globe, 
  HelpCircle, 
  CheckCircle2, 
  Clock, 
  RefreshCw, 
  ShieldCheck, 
  ArrowLeft,
  Sparkles
} from 'lucide-react';

export const Register = () => {
  const { completeAuthSession, continueAsGuest } = useAuth();
  const { t } = useLanguage();
  const { showToast } = useAppData ? useAppData() : { showToast: () => {} };
  const navigate = useNavigate();

  // Form State (Step 1)
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [userType, setUserType] = useState("Citizen");
  const [preferredLanguage, setPreferredLanguage] = useState("en");
  const [formError, setFormError] = useState("");
  const [isSubmittingForm, setIsSubmittingForm] = useState(false);

  // Verification State (Step 2)
  const [step, setStep] = useState("details"); // 'details' | 'verification'
  const [sessionData, setSessionData] = useState(null); // { sessionId, maskedEmail, maskedPhone, cooldownSeconds }
  
  const [emailOtp, setEmailOtp] = useState("");
  const [phoneOtp, setPhoneOtp] = useState("");
  const [emailVerified, setEmailVerified] = useState(false);
  const [phoneVerified, setPhoneVerified] = useState(false);
  
  const [emailError, setEmailError] = useState("");
  const [phoneError, setPhoneError] = useState("");
  const [emailSuccess, setEmailSuccess] = useState("");
  const [phoneSuccess, setPhoneSuccess] = useState("");
  
  const [isVerifyingEmail, setIsVerifyingEmail] = useState(false);
  const [isVerifyingPhone, setIsVerifyingPhone] = useState(false);
  
  const [emailCooldown, setEmailCooldown] = useState(60);
  const [phoneCooldown, setPhoneCooldown] = useState(60);
  const [isResendingEmail, setIsResendingEmail] = useState(false);
  const [isResendingPhone, setIsResendingPhone] = useState(false);

  const [registrationCompleted, setRegistrationCompleted] = useState(false);

  // Resend cooldown countdown timers
  useEffect(() => {
    let timer;
    if (step === 'verification') {
      timer = setInterval(() => {
        setEmailCooldown((prev) => (prev > 0 ? prev - 1 : 0));
        setPhoneCooldown((prev) => (prev > 0 ? prev - 1 : 0));
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [step]);

  // Step 1: Submit Details & Request OTPs
  const handleDetailsSubmit = async (e) => {
    e.preventDefault();
    setFormError("");

    if (!name.trim() || !email.trim() || !phone.trim() || !password || !confirmPassword) {
      setFormError("Please fill in all required fields.");
      return;
    }

    if (password !== confirmPassword) {
      setFormError("Passwords do not match.");
      return;
    }

    if (password.length < 6) {
      setFormError("Password must be at least 6 characters.");
      return;
    }

    setIsSubmittingForm(true);
    try {
      const res = await authService.initiateRegistration({
        name,
        email,
        phone,
        password,
        userType,
        preferredLanguage,
      });

      setSessionData(res);
      setEmailVerified(false);
      setPhoneVerified(false);
      setEmailOtp("");
      setPhoneOtp("");
      setEmailCooldown(res.cooldownSeconds || 60);
      setPhoneCooldown(res.cooldownSeconds || 60);
      setStep("verification");
      if (showToast) {
        showToast("Verification codes sent to your email and phone!", "info");
      }
    } catch (err) {
      setFormError(err.message || "Failed to initiate registration. Please check your details.");
    } finally {
      setIsSubmittingForm(false);
    }
  };

  // Step 2a: Verify Email OTP
  const handleVerifyEmail = async (e) => {
    e.preventDefault();
    setEmailError("");
    setEmailSuccess("");

    const cleanOtp = emailOtp.trim();
    if (!cleanOtp || cleanOtp.length < 4) {
      setEmailError("Please enter the verification code sent to your email.");
      return;
    }

    setIsVerifyingEmail(true);
    try {
      const res = await authService.verifyEmailOtp({
        sessionId: sessionData.sessionId,
        otp: cleanOtp,
      });

      setEmailVerified(true);
      setEmailSuccess(res.message || "Email verified successfully!");

      if (res.registrationCompleted) {
        handleFinalCompletion(res);
      }
    } catch (err) {
      setEmailError(err.message || "Invalid or expired email verification code.");
    } finally {
      setIsVerifyingEmail(false);
    }
  };

  // Step 2b: Verify Phone OTP
  const handleVerifyPhone = async (e) => {
    e.preventDefault();
    setPhoneError("");
    setPhoneSuccess("");

    const cleanOtp = phoneOtp.trim();
    if (!cleanOtp || cleanOtp.length < 4) {
      setPhoneError("Please enter the verification code sent to your phone.");
      return;
    }

    setIsVerifyingPhone(true);
    try {
      const res = await authService.verifyPhoneOtp({
        sessionId: sessionData.sessionId,
        otp: cleanOtp,
      });

      setPhoneVerified(true);
      setPhoneSuccess(res.message || "Phone number verified successfully!");

      if (res.registrationCompleted) {
        handleFinalCompletion(res);
      }
    } catch (err) {
      setPhoneError(err.message || "Invalid or expired phone verification code.");
    } finally {
      setIsVerifyingPhone(false);
    }
  };

  // Handle final completion when both factors are verified
  const handleFinalCompletion = (res) => {
    setRegistrationCompleted(true);
    if (completeAuthSession) {
      completeAuthSession(res);
    }
    if (showToast) {
      showToast("Registration successful! Welcome to Sahakar Sahayak.", "success");
    }
    setTimeout(() => {
      navigate('/dashboard');
    }, 1500);
  };

  // Resend Email OTP
  const handleResendEmail = async () => {
    if (emailCooldown > 0 || isResendingEmail || emailVerified) return;
    setIsResendingEmail(true);
    setEmailError("");
    setEmailSuccess("");

    try {
      const res = await authService.resendOtp({
        sessionId: sessionData.sessionId,
        target: 'email',
      });
      setEmailCooldown(res.cooldownSeconds || 60);
      setEmailSuccess(res.message || "A fresh code has been sent to your email.");
    } catch (err) {
      setEmailError(err.message || "Failed to resend code. Please try again.");
    } finally {
      setIsResendingEmail(false);
    }
  };

  // Resend Phone OTP
  const handleResendPhone = async () => {
    if (phoneCooldown > 0 || isResendingPhone || phoneVerified) return;
    setIsResendingPhone(true);
    setPhoneError("");
    setPhoneSuccess("");

    try {
      const res = await authService.resendOtp({
        sessionId: sessionData.sessionId,
        target: 'phone',
      });
      setPhoneCooldown(res.cooldownSeconds || 60);
      setPhoneSuccess(res.message || "A fresh code has been sent to your phone.");
    } catch (err) {
      setPhoneError(err.message || "Failed to resend code. Please try again.");
    } finally {
      setIsResendingPhone(false);
    }
  };

  const handleGuestLogin = () => {
    continueAsGuest();
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col justify-center py-10 sm:px-6 lg:px-8 transition-colors duration-150">
      <div className="sm:mx-auto sm:w-full sm:max-w-xl flex flex-col items-center">
        <Link to="/">
          <Logo className="h-12 w-12" />
        </Link>
        <h2 className="mt-4 text-center text-2xl font-black font-display text-slate-850 dark:text-white">
          {step === "details" ? "Create your account" : "Verify Email & Phone"}
        </h2>
        <p className="mt-1 text-center text-xs text-slate-500 dark:text-slate-400 max-w-md">
          {step === "details"
            ? "Join Sahakar Sahayak to access personalized cooperative dashboards and legal answers."
            : "Both your email and mobile number must be verified to activate your account."}
        </p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-xl px-4 sm:px-0">
        <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 py-8 px-6 sm:px-10 rounded-2xl shadow-sm transition-colors">

          {/* ========================================================= */}
          {/* STEP 1: REGISTRATION DETAILS FORM                         */}
          {/* ========================================================= */}
          {step === "details" && (
            <>
              {formError && (
                <div className="mb-5 p-3 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/40 text-xs font-semibold text-red-600 dark:text-red-400 rounded-lg animate-message-appear">
                  {formError}
                </div>
              )}

              <form className="space-y-4" onSubmit={handleDetailsSubmit}>
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

                {/* Email Address */}
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
                      placeholder="name@example.gov.in"
                      className="w-full pl-9.5 pr-4 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-slate-800 dark:text-slate-100 placeholder-slate-450 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 dark:focus:border-primary-400 text-sm transition-all"
                    />
                  </div>
                </div>

                {/* Phone Number */}
                <div className="space-y-1.5">
                  <label htmlFor="phone" className="block text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                    {t('phoneNumber')}
                  </label>
                  <div className="relative flex items-center">
                    <Phone className="absolute left-3 h-4 w-4 text-slate-400" />
                    <input
                      id="phone"
                      type="tel"
                      required
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      placeholder="+91 9876543210 or 9876543210"
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
                      {t('confirmPassword')}
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

                {/* Submit button */}
                <button
                  type="submit"
                  disabled={isSubmittingForm}
                  className="w-full inline-flex items-center justify-center gap-2 py-2.5 border border-transparent rounded-lg text-sm font-bold text-white bg-primary-600 hover:bg-primary-700 dark:bg-primary-600 dark:hover:bg-primary-700 shadow-md shadow-primary-500/10 hover:translate-y-[-1px] active:translate-y-[0] transition-all cursor-pointer disabled:opacity-60"
                >
                  <ShieldCheck className="h-4.5 w-4.5" />
                  <span>{isSubmittingForm ? "Sending Verification Codes..." : "Continue to Verification"}</span>
                </button>
              </form>

              {/* Spacer */}
              <div className="relative my-5">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-slate-200 dark:border-slate-800" />
                </div>
                <div className="relative flex justify-center text-xs">
                  <span className="bg-white dark:bg-slate-900 px-3 text-slate-400 dark:text-slate-550">
                    Or explore without credentials
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
                <Link to="/login" className="text-xs font-bold text-primary-600 hover:text-primary-700 dark:text-primary-400">
                  {t('alreadyHaveAccount')}
                </Link>
              </div>
            </>
          )}

          {/* ========================================================= */}
          {/* STEP 2: DUAL OTP VERIFICATION (EMAIL & PHONE)             */}
          {/* ========================================================= */}
          {step === "verification" && (
            <div className="space-y-6">
              {/* Status Header Overview */}
              <div className="bg-slate-50 dark:bg-slate-950 p-4 rounded-xl border border-slate-200/80 dark:border-slate-800">
                <div className="flex items-center justify-between flex-wrap gap-2 text-xs font-bold">
                  <span className="text-slate-600 dark:text-slate-300 uppercase tracking-wider">
                    Verification Status:
                  </span>
                  <div className="flex items-center gap-3">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${
                      emailVerified 
                        ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800" 
                        : "bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300 border border-amber-300 dark:border-amber-800"
                    }`}>
                      {emailVerified ? <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" /> : <Clock className="h-3.5 w-3.5 text-amber-500" />}
                      <span>Email: {emailVerified ? "✓ Verified" : "Pending"}</span>
                    </span>

                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${
                      phoneVerified 
                        ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800" 
                        : "bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300 border border-amber-300 dark:border-amber-800"
                    }`}>
                      {phoneVerified ? <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" /> : <Clock className="h-3.5 w-3.5 text-amber-500" />}
                      <span>Phone: {phoneVerified ? "✓ Verified" : "Pending"}</span>
                    </span>
                  </div>
                </div>

                {/* Progress bar */}
                <div className="w-full bg-slate-200 dark:bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
                  <div 
                    className="bg-emerald-600 h-full transition-all duration-300"
                    style={{ width: emailVerified && phoneVerified ? '100%' : (emailVerified || phoneVerified ? '50%' : '5%') }}
                  />
                </div>
              </div>

              {registrationCompleted ? (
                <div className="p-6 bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800 rounded-xl text-center space-y-3 animate-message-appear">
                  <div className="inline-flex items-center justify-center h-12 w-12 rounded-full bg-emerald-100 dark:bg-emerald-900/60 text-emerald-600 dark:text-emerald-400">
                    <Sparkles className="h-6 w-6" />
                  </div>
                  <h3 className="text-base font-bold text-emerald-900 dark:text-emerald-100">
                    Account Successfully Activated!
                  </h3>
                  <p className="text-xs text-emerald-700 dark:text-emerald-300">
                    Both Email and Phone Number verified. Redirecting you to the dashboard...
                  </p>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* ================================================= */}
                  {/* CARD 1: EMAIL OTP VERIFICATION                   */}
                  {/* ================================================= */}
                  <div className={`p-4 sm:p-5 rounded-xl border transition-all ${
                    emailVerified 
                      ? "bg-emerald-50/50 dark:bg-emerald-950/10 border-emerald-200 dark:border-emerald-900/40" 
                      : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800"
                  }`}>
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <Mail className={`h-4.5 w-4.5 ${emailVerified ? "text-emerald-600" : "text-primary-600"}`} />
                        <span className="text-sm font-bold text-slate-800 dark:text-white">
                          Email Verification
                        </span>
                      </div>
                      <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                        emailVerified 
                          ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/60 dark:text-emerald-200" 
                          : "bg-amber-100 text-amber-800 dark:bg-amber-900/60 dark:text-amber-200"
                      }`}>
                        {emailVerified ? "✓ Verified" : "Action Required"}
                      </span>
                    </div>

                    <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">
                      Code sent to: <strong className="text-slate-700 dark:text-slate-200">{sessionData?.maskedEmail || email}</strong>
                    </p>

                    {emailError && (
                      <div className="mb-3 p-2.5 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/40 text-xs font-semibold text-red-600 dark:text-red-400 rounded-lg">
                        {emailError}
                      </div>
                    )}

                    {emailSuccess && (
                      <div className="mb-3 p-2.5 bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-900/40 text-xs font-semibold text-emerald-600 dark:text-emerald-400 rounded-lg">
                        {emailSuccess}
                      </div>
                    )}

                    {emailVerified ? (
                      <div className="flex items-center gap-2 text-xs font-semibold text-emerald-600 dark:text-emerald-400 py-1">
                        <CheckCircle2 className="h-4 w-4" />
                        <span>Email address verified successfully.</span>
                      </div>
                    ) : (
                      <form onSubmit={handleVerifyEmail} className="space-y-3">
                        <div className="flex gap-2">
                          <input
                            type="text"
                            maxLength={6}
                            required
                            value={emailOtp}
                            onChange={(e) => setEmailOtp(e.target.value.replace(/\D/g, ''))}
                            placeholder="6-digit Email OTP"
                            className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-slate-800 dark:text-slate-100 font-mono tracking-widest text-center text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
                          />
                          <button
                            type="submit"
                            disabled={isVerifyingEmail || emailOtp.length < 4}
                            className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-xs font-bold shadow-sm transition-all disabled:opacity-50 cursor-pointer whitespace-nowrap"
                          >
                            {isVerifyingEmail ? "Checking..." : "Verify Email"}
                          </button>
                        </div>

                        <div className="flex items-center justify-between text-xs pt-1">
                          <span className="text-slate-400 dark:text-slate-500 text-[11px]">Valid for 10 minutes</span>
                          <button
                            type="button"
                            onClick={handleResendEmail}
                            disabled={emailCooldown > 0 || isResendingEmail}
                            className="inline-flex items-center gap-1 text-primary-600 hover:text-primary-700 dark:text-primary-400 font-bold disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                          >
                            <RefreshCw className={`h-3 w-3 ${isResendingEmail ? "animate-spin" : ""}`} />
                            <span>
                              {emailCooldown > 0 ? `Resend OTP (${emailCooldown}s)` : "Resend Email OTP"}
                            </span>
                          </button>
                        </div>
                      </form>
                    )}
                  </div>

                  {/* ================================================= */}
                  {/* CARD 2: PHONE OTP VERIFICATION                   */}
                  {/* ================================================= */}
                  <div className={`p-4 sm:p-5 rounded-xl border transition-all ${
                    phoneVerified 
                      ? "bg-emerald-50/50 dark:bg-emerald-950/10 border-emerald-200 dark:border-emerald-900/40" 
                      : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800"
                  }`}>
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <Phone className={`h-4.5 w-4.5 ${phoneVerified ? "text-emerald-600" : "text-primary-600"}`} />
                        <span className="text-sm font-bold text-slate-800 dark:text-white">
                          Phone Verification
                        </span>
                      </div>
                      <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                        phoneVerified 
                          ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/60 dark:text-emerald-200" 
                          : "bg-amber-100 text-amber-800 dark:bg-amber-900/60 dark:text-amber-200"
                      }`}>
                        {phoneVerified ? "✓ Verified" : "Action Required"}
                      </span>
                    </div>

                    <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">
                      Code sent to: <strong className="text-slate-700 dark:text-slate-200">{sessionData?.maskedPhone || phone}</strong>
                    </p>

                    {phoneError && (
                      <div className="mb-3 p-2.5 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/40 text-xs font-semibold text-red-600 dark:text-red-400 rounded-lg">
                        {phoneError}
                      </div>
                    )}

                    {phoneSuccess && (
                      <div className="mb-3 p-2.5 bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-900/40 text-xs font-semibold text-emerald-600 dark:text-emerald-400 rounded-lg">
                        {phoneSuccess}
                      </div>
                    )}

                    {phoneVerified ? (
                      <div className="flex items-center gap-2 text-xs font-semibold text-emerald-600 dark:text-emerald-400 py-1">
                        <CheckCircle2 className="h-4 w-4" />
                        <span>Phone number verified successfully.</span>
                      </div>
                    ) : (
                      <form onSubmit={handleVerifyPhone} className="space-y-3">
                        <div className="flex gap-2">
                          <input
                            type="text"
                            maxLength={6}
                            required
                            value={phoneOtp}
                            onChange={(e) => setPhoneOtp(e.target.value.replace(/\D/g, ''))}
                            placeholder="6-digit Phone OTP"
                            className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-slate-800 dark:text-slate-100 font-mono tracking-widest text-center text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
                          />
                          <button
                            type="submit"
                            disabled={isVerifyingPhone || phoneOtp.length < 4}
                            className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-xs font-bold shadow-sm transition-all disabled:opacity-50 cursor-pointer whitespace-nowrap"
                          >
                            {isVerifyingPhone ? "Checking..." : "Verify Phone"}
                          </button>
                        </div>

                        <div className="flex items-center justify-between text-xs pt-1">
                          <span className="text-slate-400 dark:text-slate-500 text-[11px]">Valid for 10 minutes</span>
                          <button
                            type="button"
                            onClick={handleResendPhone}
                            disabled={phoneCooldown > 0 || isResendingPhone}
                            className="inline-flex items-center gap-1 text-primary-600 hover:text-primary-700 dark:text-primary-400 font-bold disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                          >
                            <RefreshCw className={`h-3 w-3 ${isResendingPhone ? "animate-spin" : ""}`} />
                            <span>
                              {phoneCooldown > 0 ? `Resend OTP (${phoneCooldown}s)` : "Resend Phone OTP"}
                            </span>
                          </button>
                        </div>
                      </form>
                    )}
                  </div>
                </div>
              )}

              {/* Navigation Actions */}
              <div className="pt-2 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs">
                <button
                  type="button"
                  onClick={() => setStep("details")}
                  className="inline-flex items-center gap-1.5 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 font-semibold cursor-pointer"
                >
                  <ArrowLeft className="h-3.5 w-3.5" />
                  <span>Back to Edit Details</span>
                </button>

                <Link to="/login" className="font-bold text-primary-600 hover:text-primary-700 dark:text-primary-400">
                  {t('alreadyHaveAccount')}
                </Link>
              </div>

            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default Register;
