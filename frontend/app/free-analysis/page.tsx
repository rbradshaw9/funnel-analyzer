'use client';

import { useEffect, useMemo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { analyzeFunnel, sendAnalysisEmail } from '@/lib/api';
import type { AnalysisResult } from '@/types';
import { TopNav } from '@/components/TopNav';
import { SMART_TOOL_CLUB_JOIN_URL } from '@/lib/externalLinks';

type StageKey = 'scrape' | 'screenshot' | 'analysis' | 'summary';

const STAGE_SEQUENCE: Array<{ key: StageKey; label: string; message: string }> = [
  {
    key: 'scrape',
    label: 'Content scraping',
    message: 'Scraping your page content…',
  },
  {
    key: 'screenshot',
    label: 'Screenshots',
    message: 'Capturing screenshots & structure…',
  },
  {
    key: 'analysis',
    label: 'LLM analysis',
    message: 'Evaluating copy, design, and proof…',
  },
  {
    key: 'summary',
    label: 'Report summary',
    message: 'Preparing executive summary & next steps…',
  },
];

const DEFAULT_STAGE_ESTIMATES: Record<StageKey, number> = {
  scrape: 3.0,
  screenshot: 5.0,
  analysis: 13.5,
  summary: 6.5,
};

const STORAGE_KEY_STAGE_ESTIMATES = 'faStageEstimates';
const MIN_STAGE_SECONDS = 0.8;
const MAX_STAGE_SECONDS = 60;

const clampDuration = (value: unknown, fallback: number) => {
  const numeric = typeof value === 'number' && Number.isFinite(value) ? value : fallback;
  return Math.min(Math.max(numeric, MIN_STAGE_SECONDS), MAX_STAGE_SECONDS);
};

const smoothDuration = (previous: number, next: number) => {
  const blended = previous * 0.6 + next * 0.4;
  return Math.round(blended * 100) / 100;
};

const sumDurations = (estimates: Record<StageKey, number>) =>
  STAGE_SEQUENCE.reduce((total, stage) => total + Math.max(estimates[stage.key], MIN_STAGE_SECONDS), 0);

const formatSeconds = (value?: number | null) => {
  if (typeof value !== 'number' || !Number.isFinite(value) || value <= 0) return '—';
  if (value >= 60) {
    const minutes = Math.floor(value / 60);
    const seconds = Math.round(value % 60);
    if (seconds === 0) {
      return `${minutes}m`;
    }
    return `${minutes}m ${seconds}s`;
  }
  if (value >= 10) {
    return `${Math.round(value)}s`;
  }
  return `${value.toFixed(1)}s`;
};

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
  const [stageEstimates, setStageEstimates] = useState<Record<StageKey, number>>(() => ({
    ...DEFAULT_STAGE_ESTIMATES,
  }));

  const estimatedTotalSeconds = useMemo(() => sumDurations(stageEstimates), [stageEstimates]);

  const progressStages = useMemo(() => {
    const stagesWithDurations = STAGE_SEQUENCE.map((stage) => ({
      ...stage,
      seconds: Math.max(stageEstimates[stage.key], MIN_STAGE_SECONDS),
    }));

    const totalSeconds = stagesWithDurations.reduce((acc, stage) => acc + stage.seconds, 0);
    let elapsed = 0;

    return stagesWithDurations.map((stage, index) => {
      elapsed += stage.seconds;
      const ratio = totalSeconds > 0 ? elapsed / totalSeconds : (index + 1) / stagesWithDurations.length;
      const percentBase = 18 + ratio * 75;
      const percent = Math.min(Math.round(percentBase), index === stagesWithDurations.length - 1 ? 96 : 95);
      const delay = Math.max(750, Math.round(elapsed * 1000));

      return {
        key: stage.key,
        delay,
        percent,
        message: stage.message,
      };
    });
  }, [stageEstimates]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY_STAGE_ESTIMATES);
      if (!stored) return;
      const parsed = JSON.parse(stored) as Partial<Record<StageKey, number>>;
      setStageEstimates((previous) => ({
        scrape: clampDuration(parsed?.scrape, previous.scrape),
        screenshot: clampDuration(parsed?.screenshot, previous.screenshot),
        analysis: clampDuration(parsed?.analysis, previous.analysis),
        summary: clampDuration(parsed?.summary, previous.summary),
      }));
    } catch (error) {
      console.warn('Failed to load stage estimates', error);
    }
  }, []);

  useEffect(() => {
    const telemetry = result?.pipeline_metrics;
    if (!telemetry?.stage_timings) return;

    const timings = telemetry.stage_timings;

    setStageEstimates((previous) => {
      const nextScrape = clampDuration(timings.scrape_seconds, previous.scrape);
      const nextScreenshot = clampDuration(timings.screenshot_seconds, previous.screenshot);
      const nextAnalysis = clampDuration(timings.analysis_seconds, previous.analysis);

      const totalCandidateRaw =
        typeof timings.total_seconds === 'number' && Number.isFinite(timings.total_seconds)
          ? timings.total_seconds
          : result?.analysis_duration_seconds;

      const totalSeconds =
        typeof totalCandidateRaw === 'number' && Number.isFinite(totalCandidateRaw) && totalCandidateRaw > 0
          ? totalCandidateRaw
          : sumDurations(previous);

      let summaryCandidate =
        totalSeconds -
        (timings.scrape_seconds ?? 0) -
        (timings.screenshot_seconds ?? 0) -
        (timings.analysis_seconds ?? 0);

      if (!Number.isFinite(summaryCandidate) || summaryCandidate <= 0) {
        summaryCandidate = previous.summary;
      }

      const nextSummary = clampDuration(summaryCandidate, previous.summary);

      const updated: Record<StageKey, number> = {
        scrape: smoothDuration(previous.scrape, nextScrape),
        screenshot: smoothDuration(previous.screenshot, nextScreenshot),
        analysis: smoothDuration(previous.analysis, nextAnalysis),
        summary: smoothDuration(previous.summary, nextSummary),
      };

      try {
        if (typeof window !== 'undefined') {
          window.localStorage.setItem(STORAGE_KEY_STAGE_ESTIMATES, JSON.stringify(updated));
        }
      } catch (error) {
        console.warn('Failed to store stage estimates', error);
      }

      return updated;
    });
  }, [result?.pipeline_metrics, result?.analysis_duration_seconds]);

  const stageTimings = result?.pipeline_metrics?.stage_timings;
  const screenshotMetrics = result?.pipeline_metrics?.screenshot;
  const telemetryNotes = result?.pipeline_metrics?.notes;
  const llmProvider = result?.pipeline_metrics?.llm_provider;
  const actualRunTimeSeconds = stageTimings?.total_seconds ?? result?.analysis_duration_seconds ?? null;
  const stageBreakdown = useMemo<Record<StageKey, number | undefined>>(() => {
    if (stageTimings) {
      const summaryCandidate =
        (stageTimings.total_seconds ?? 0) -
        (stageTimings.scrape_seconds ?? 0) -
        (stageTimings.screenshot_seconds ?? 0) -
        (stageTimings.analysis_seconds ?? 0);

      return {
        scrape: stageTimings.scrape_seconds,
        screenshot: stageTimings.screenshot_seconds,
        analysis: stageTimings.analysis_seconds,
        summary: summaryCandidate > MIN_STAGE_SECONDS ? summaryCandidate : undefined,
      };
    }

    return {
      scrape: stageEstimates.scrape,
      screenshot: stageEstimates.screenshot,
      analysis: stageEstimates.analysis,
      summary: stageEstimates.summary,
    };
  }, [stageTimings, stageEstimates]);
  const timelineSource = stageTimings ? 'actual' : 'estimated';

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
        window.location.href = SMART_TOOL_CLUB_JOIN_URL;
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
      <TopNav
        rightSlot={
          <a
            href={SMART_TOOL_CLUB_JOIN_URL}
            className="text-sm font-semibold text-indigo-600 hover:text-indigo-700"
          >
            Smart Tool Club →
          </a>
        }
      />

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
                <span>Estimated time: ~{formatSeconds(estimatedTotalSeconds)}</span>
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

              <div className="mt-2 mb-6 text-sm text-gray-500 text-center space-y-1">
                <div>
                  <span className="font-semibold text-gray-700">Actual run time:</span>{' '}
                  {formatSeconds(actualRunTimeSeconds)}
                </div>
                {llmProvider && (
                  <div>
                    <span className="font-semibold text-gray-700">LLM:</span>{' '}
                    <span className="uppercase tracking-wide text-gray-500">{llmProvider}</span>
                  </div>
                )}
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

            <div className="bg-white rounded-2xl shadow-xl p-8 mb-8 border border-gray-200">
              <div className="flex items-center justify-between mb-6">
                <h4 className="text-xl font-semibold text-gray-900">Analysis timeline</h4>
                <span className="text-xs font-semibold uppercase tracking-wide text-indigo-500/80">
                  {timelineSource === 'actual' ? 'Actual' : 'Estimated'}
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {STAGE_SEQUENCE.map((stage) => (
                  <div
                    key={stage.key}
                    className="rounded-xl border border-indigo-100 bg-indigo-50/50 p-4"
                  >
                    <div className="text-sm font-semibold text-indigo-600">{stage.label}</div>
                    <div className="text-2xl font-bold text-gray-900 mt-2">
                      {formatSeconds(stageBreakdown[stage.key])}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">{stage.message.replace(/…$/, '.')}</div>
                  </div>
                ))}
              </div>

              {screenshotMetrics && screenshotMetrics.attempted > 0 && (
                <div className="mt-6 text-sm text-gray-600 flex flex-wrap gap-x-3 gap-y-1">
                  <span className="font-semibold text-gray-700">Screenshots:</span>
                  <span>
                    {screenshotMetrics.succeeded}/{screenshotMetrics.attempted} captured
                  </span>
                  {screenshotMetrics.uploaded ? (
                    <span>· {screenshotMetrics.uploaded} uploaded</span>
                  ) : null}
                  {screenshotMetrics.timeouts ? (
                    <span>· {screenshotMetrics.timeouts} timeouts</span>
                  ) : null}
                  {screenshotMetrics.failed ? (
                    <span>· {screenshotMetrics.failed} errors</span>
                  ) : null}
                </div>
              )}

              {telemetryNotes && telemetryNotes.length > 0 && (
                <div className="mt-4 text-xs text-gray-400">
                  <span className="font-semibold text-gray-500">Notes:</span>{' '}
                  {telemetryNotes.join(', ')}
                </div>
              )}
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
                      href={SMART_TOOL_CLUB_JOIN_URL}
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
