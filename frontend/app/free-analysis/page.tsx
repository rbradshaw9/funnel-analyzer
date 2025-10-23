'use client';

import { useEffect, useMemo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { analyzeFunnel, sendAnalysisEmail } from '@/lib/api';
import type { AnalysisResult } from '@/types';

export default function FreeAnalysisPage() {
  const [url, setUrl] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [showUnlockModal, setShowUnlockModal] = useState(false);
  const [email, setEmail] = useState('');
  const [emailSubmitted, setEmailSubmitted] = useState(false);
  const [isSendingEmail, setIsSendingEmail] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('Initializing analysis…');
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  const progressStages = useMemo(
    () => [
      { delay: 1500, percent: 20, message: 'Scraping your page content…' },
      { delay: 5000, percent: 38, message: 'Capturing screenshots & structure…' },
      { delay: 11000, percent: 58, message: 'Evaluating copy, design, and proof…' },
      { delay: 20000, percent: 78, message: 'Scoring conversion opportunities…' },
      { delay: 32000, percent: 92, message: 'Preparing executive summary & next steps…' },
    ],
    []
  );

  useEffect(() => {
    if (!isAnalyzing) {
      setProgress(0);
      setProgressMessage('Initializing analysis…');
      setElapsedSeconds(0);
      return;
    }

    setProgress(8);
    setProgressMessage('Queueing your analysis…');
    setElapsedSeconds(0);

    const timers = progressStages.map(({ delay, percent, message }) =>
      setTimeout(() => {
        setProgress(percent);
        setProgressMessage(message);
      }, delay)
    );

    const interval = setInterval(() => {
      setElapsedSeconds((seconds) => seconds + 1);
    }, 1000);

    return () => {
      timers.forEach(clearTimeout);
      clearInterval(interval);
    };
  }, [isAnalyzing, progressStages]);

  const handleAnalyze = async () => {
    if (!url.trim()) return;

    setIsAnalyzing(true);
    setProgress(8);
    setProgressMessage('Queueing your analysis…');
    setResult(null);
    setEmailSubmitted(false);
    setShowUnlockModal(false);

    try {
      const analysis = await analyzeFunnel([url.trim()]);
      setResult(analysis);
      setEmail(analysis.recipient_email ?? '');
      setProgress(100);
      setProgressMessage('Analysis ready!');
    } catch (error) {
      console.error('Analysis failed:', error);
      alert('Analysis failed. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleUnlockReport = async () => {
    if (!result) {
      alert('Run an analysis first to unlock the report.');
      return;
    }

    if (!email.trim() || !email.includes('@')) {
      alert('Please enter a valid email address');
      return;
    }

    try {
      setIsSendingEmail(true);
  await sendAnalysisEmail(result.analysis_id, email.trim());
  setEmailSubmitted(true);
  setEmail(email.trim());
  setResult((prev) => (prev ? { ...prev, recipient_email: email.trim() } : prev));

      setTimeout(() => {
        window.location.href = 'https://smarttoolclub.com/join';
      }, 3000);
    } catch (err) {
      console.error('Failed to send analysis email:', err);
      alert(
        err instanceof Error
          ? err.message
          : 'We could not email the full report. Please try again shortly.'
      );
    } finally {
      setIsSendingEmail(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return 'text-green-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreGradient = (score: number) => {
    if (score >= 70) return 'from-green-500 to-green-600';
    if (score >= 40) return 'from-yellow-500 to-yellow-600';
    return 'from-red-500 to-red-600';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              Funnel Analyzer Pro
            </h1>
            <a
              href="https://smarttoolclub.com"
              className="text-sm font-medium text-indigo-600 hover:text-indigo-700"
            >
              Smart Tool Club →
            </a>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        {!result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center max-w-3xl mx-auto mb-12"
          >
            <h2 className="text-5xl font-extrabold text-gray-900 mb-6">
              Get Your Free
              <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                {' '}Marketing Page Analysis
              </span>
            </h2>
            <p className="text-xl text-gray-600 mb-8">
              AI-powered insights to optimize your sales pages, landing pages, and funnels.
              Get instant feedback on clarity, design, and conversion potential.
            </p>

            {/* URL Input */}
            <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-200">
              <label htmlFor="url" className="block text-left text-sm font-semibold text-gray-700 mb-3">
                Enter your page URL
              </label>
              <div className="flex gap-3">
                <input
                  id="url"
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAnalyze()}
                  placeholder="https://example.com/your-page"
                  className="flex-1 px-4 py-4 text-lg border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                  disabled={isAnalyzing}
                />
                <button
                  onClick={handleAnalyze}
                  disabled={isAnalyzing || !url.trim()}
                  className="px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold rounded-xl hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
                >
                  {isAnalyzing ? 'Analyzing...' : 'Analyze Free'}
                </button>
              </div>
              <p className="text-sm text-gray-500 mt-3 text-left">
                ✨ No signup required • 💯 100% free analysis • ⚡ Results in seconds
              </p>
            </div>

            {/* Trust Signals */}
            <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
              <div>
                <div className="text-3xl font-bold text-indigo-600">500+</div>
                <div className="text-sm text-gray-600">Pages Analyzed</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-indigo-600">AI-Powered</div>
                <div className="text-sm text-gray-600">GPT-4o Analysis</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-indigo-600">Instant</div>
                <div className="text-sm text-gray-600">Results</div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Loading State */}
        {isAnalyzing && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-20"
          >
            <div className="max-w-xl mx-auto bg-white rounded-2xl shadow-xl border border-indigo-100 p-8">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-2xl font-bold text-gray-900">Analyzing Your Page…</h3>
                <span className="text-sm font-medium text-indigo-600">
                  {elapsedSeconds}s elapsed
                </span>
              </div>
              <p className="text-gray-600 mb-6">{progressMessage}</p>
              <div className="h-3 w-full bg-indigo-100 rounded-full overflow-hidden">
                <motion.div
                  key={progress}
                  initial={{ width: `${Math.max(progress - 10, 0)}%` }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.6, ease: 'easeOut' }}
                  className="h-full bg-gradient-to-r from-indigo-500 to-purple-600"
                />
              </div>
              <div className="mt-4 flex items-center justify-between text-sm text-gray-500">
                <span>Estimated time: ~45 seconds</span>
                <span className="font-medium text-indigo-600">Hang tight — almost there!</span>
              </div>
            </div>
          </motion.div>
        )}

        {/* Results */}
        {result && !isAnalyzing && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-4xl mx-auto"
          >
            {/* Overall Score */}
            <div className="bg-white rounded-2xl shadow-xl p-8 mb-8 border border-gray-200">
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-4">Your Page Score</h3>
                <div className="relative inline-block">
                  <svg className="w-48 h-48 transform -rotate-90">
                    <circle
                      cx="96"
                      cy="96"
                      r="88"
                      stroke="#e5e7eb"
                      strokeWidth="16"
                      fill="none"
                    />
                    <circle
                      cx="96"
                      cy="96"
                      r="88"
                      stroke="url(#scoreGradient)"
                      strokeWidth="16"
                      fill="none"
                      strokeDasharray={`${(result.overall_score / 100) * 553} 553`}
                      strokeLinecap="round"
                    />
                    <defs>
                      <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" className="text-indigo-600" stopColor="currentColor" />
                        <stop offset="100%" className="text-purple-600" stopColor="currentColor" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div>
                      <div className={`text-6xl font-extrabold ${getScoreColor(result.overall_score)}`}>
                        {result.overall_score}
                      </div>
                      <div className="text-sm text-gray-500 font-medium">out of 100</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Score Breakdown */}
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
                {Object.entries(result.scores).map(([key, value]) => (
                  <div key={key} className="text-center">
                    <div className={`text-3xl font-bold ${getScoreColor(value)}`}>{value}</div>
                    <div className="text-sm text-gray-600 capitalize">{key}</div>
                  </div>
                ))}
              </div>

              {/* Blurred Summary */}
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-b from-transparent via-white/50 to-white z-10 backdrop-blur-sm rounded-lg"></div>
                <div className="filter blur-sm select-none pointer-events-none">
                  <h4 className="font-semibold text-gray-900 mb-2">Executive Summary</h4>
                  <p className="text-gray-600 leading-relaxed">{result.summary}</p>
                </div>
                
                {/* Unlock Button Overlay */}
                <div className="absolute inset-0 flex items-center justify-center z-20">
                  <button
                    onClick={() => setShowUnlockModal(true)}
                    className="px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all shadow-2xl hover:shadow-3xl hover:scale-105"
                  >
                    🔓 Unlock Full Report
                  </button>
                </div>
              </div>
            </div>

            {/* Blurred Detailed Feedback */}
            <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-200 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-b from-transparent via-white/70 to-white z-10 backdrop-blur-md"></div>
              <div className="filter blur-md select-none pointer-events-none">
                <h4 className="font-semibold text-gray-900 mb-4">Detailed Analysis</h4>
                {result.pages.map((page, idx) => (
                  <div key={idx} className="mb-6">
                    <h5 className="font-medium text-gray-700 mb-2">{page.title}</h5>
                    <p className="text-gray-600">{page.feedback}</p>
                  </div>
                ))}
              </div>
              
              <div className="absolute inset-0 flex items-center justify-center z-20">
                <div className="text-center bg-white/90 backdrop-blur-sm rounded-2xl p-8 shadow-2xl max-w-md">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">
                    Want the Full Analysis?
                  </h3>
                  <p className="text-gray-600 mb-6">
                    Get detailed insights, actionable recommendations, and access to unlimited analyses.
                  </p>
                  <button
                    onClick={() => setShowUnlockModal(true)}
                    className="px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all shadow-xl hover:scale-105"
                  >
                    Unlock Now →
                  </button>
                </div>
              </div>
            </div>

            {/* Try Another */}
            <div className="text-center mt-8">
              <button
                onClick={() => {
                  setResult(null);
                  setUrl('');
                }}
                className="text-indigo-600 hover:text-indigo-700 font-medium"
              >
                ← Analyze Another Page
              </button>
            </div>
          </motion.div>
        )}
      </main>

      {/* Unlock Modal */}
      <AnimatePresence>
        {showUnlockModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={() => setShowUnlockModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8"
            >
              {!emailSubmitted ? (
                <>
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">Unlock Your Full Report</h3>
                  <p className="text-gray-600 mb-6">
                    Enter your email to receive the complete analysis with detailed recommendations.
                  </p>

                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="your@email.com"
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent mb-4"
                  />

                  <button
                    onClick={handleUnlockReport}
                    disabled={isSendingEmail}
                    className="w-full px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all shadow-lg mb-3 disabled:opacity-60 disabled:cursor-not-allowed"
                  >
                    {isSendingEmail ? 'Sending…' : 'Send Me the Full Report'}
                  </button>

                  <div className="text-center">
                    <p className="text-sm text-gray-500 mb-3">or</p>
                    <a
                      href="https://smarttoolclub.com/join"
                      className="text-indigo-600 hover:text-indigo-700 font-semibold"
                    >
                      Join Smart Tool Club for Unlimited Access →
                    </a>
                  </div>

                  <p className="text-xs text-gray-400 mt-6 text-center">
                    We respect your privacy. Unsubscribe anytime.
                  </p>
                </>
              ) : (
                <div className="text-center py-8">
                  <div className="text-6xl mb-4">✅</div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">Check Your Email!</h3>
                  <p className="text-gray-600 mb-6">
                    We&apos;ve sent the full report to <strong>{email}</strong>
                  </p>
                  <p className="text-sm text-gray-500">
                    Redirecting to Smart Tool Club membership...
                  </p>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
