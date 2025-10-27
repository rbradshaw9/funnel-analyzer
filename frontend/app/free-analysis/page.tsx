'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { analyzeFunnel } from '@/lib/api';
import type { AnalysisResult } from '@/types';
import { TopNav } from '@/components/TopNav';
import { FUNNEL_ANALYZER_JOIN_URL } from '@/lib/externalLinks';
import { useAuthValidation } from '@/hooks/useAuthValidation';
import { AuthModal, type AuthMode } from '@/components/AuthModal';
import { AuthPromptCard } from '@/components/AuthPromptCard';
import { useAuthStore } from '@/store/authStore';

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

const UPGRADE_FEATURES: Array<{ title: string; description: string }> = [

  {
    title: 'Unlimited funnel steps',
    description: 'Audit every page in your funnel with side-by-side drop-off tracking.',
  },
  {
    title: 'AI rewrite playbooks',
    description: 'Instant headline, hook, and CTA rewrites tuned to your niche.',
  },
  {
    title: 'Competitor benchmarking',
    description: 'See how you stack up against top-performing funnels in your industry.',
  },
  {
    title: 'Client-ready exports',
    description: 'Generate polished PDF and slide exports for teams and stakeholders.',
  },
];

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
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authModalMode, setAuthModalMode] = useState<AuthMode>('signup');
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('Initializing analysis…');
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [stageEstimates, setStageEstimates] = useState<Record<StageKey, number>>(() => ({
    ...DEFAULT_STAGE_ESTIMATES,
  }));

  const resetAuth = useAuthStore((state) => state.reset);

  const {
    token: authToken,
    loading: authLoading,
    error: authError,
    accessGranted,
    statusMessage: authStatusMessage,
    statusReason: authStatusReason,
    userId,
  } = useAuthValidation();

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
    const sanitizedUrl = url.trim().split(/\s+/)[0] ?? '';
    if (!sanitizedUrl) return;

    setIsAnalyzing(true);
    setProgress(8);
    setProgressMessage('Queueing your analysis…');
    setResult(null);

    try {
      setUrl(sanitizedUrl);
      const analysis = await analyzeFunnel([sanitizedUrl], {
        userId: typeof userId === 'number' ? userId : undefined,
        token: authToken ?? undefined,
      });
      setResult(analysis);
      setProgress(100);
      setProgressMessage('Analysis ready!');
    } catch (error) {
      console.error('Analysis failed:', error);
      alert('Analysis failed. Please try again.');
    } finally {
      setIsAnalyzing(false);
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

  const canViewFullContent = Boolean(authToken && accessGranted);
  const showAuthPrompt = !canViewFullContent;
  const promptStatusMessage = (() => {
    if (authToken) {
      if (authLoading) {
        return 'Verifying your membership…';
      }
      if (!accessGranted) {
        return authStatusMessage || authStatusReason || 'Your membership needs attention.';
      }
      return null;
    }
    return 'Create a free account to unlock the full analysis.';
  })();
  const promptErrorMessage = authError ?? null;
  const promptDisabled = authLoading && Boolean(authToken);

  const openAuthModal = (mode: AuthMode) => {
    setAuthModalMode(mode);
    setAuthModalOpen(true);
  };

  const handleSignOut = () => {
    resetAuth();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-accent-50">
      {/* Header */}
      <TopNav
        rightSlot={
          <Link
            href={FUNNEL_ANALYZER_JOIN_URL}
            className="text-sm font-semibold text-primary-600 hover:text-primary-700"
          >
            Pricing →
          </Link>
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
              <span className="bg-gradient-to-r from-primary-600 to-accent-500 bg-clip-text text-transparent">
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
                  className="flex-1 px-4 py-4 text-lg border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                  disabled={isAnalyzing}
                />
                <button
                  onClick={handleAnalyze}
                  disabled={isAnalyzing || !url.trim()}
                  className="px-8 py-4 bg-gradient-to-r from-primary-600 to-accent-500 text-white font-bold rounded-xl hover:from-primary-700 hover:to-accent-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
                >
                  {isAnalyzing ? 'Analyzing...' : 'Analyze Free'}
                </button>
              </div>
              <p className="text-sm text-gray-500 mt-3 text-left">
                ✨ No signup required • � Covers your primary page only • ⚡ Results in seconds
              </p>
            </div>

            {/* Trust Signals */}
            <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
              <div>
                <div className="text-3xl font-bold text-primary-600">500+</div>
                <div className="text-sm text-gray-600">Pages Analyzed</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-accent-500">AI-Powered</div>
                <div className="text-sm text-gray-600">GPT-4o Analysis</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-primary-600">Instant</div>
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
            <div className="max-w-xl mx-auto bg-white rounded-2xl shadow-xl border border-primary-100 p-8">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-2xl font-bold text-gray-900">Analyzing Your Page…</h3>
                <span className="text-sm font-medium text-primary-600">
                  {elapsedSeconds}s elapsed
                </span>
              </div>
              <p className="text-gray-600 mb-6">{progressMessage}</p>
              <div className="h-3 w-full bg-primary-100 rounded-full overflow-hidden">
                <motion.div
                  key={progress}
                  initial={{ width: `${Math.max(progress - 10, 0)}%` }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.6, ease: 'easeOut' }}
                  className="h-full bg-gradient-to-r from-primary-500 to-accent-500"
                />
              </div>
              <div className="mt-4 flex items-center justify-between text-sm text-gray-500">
                <span>Estimated time: ~{formatSeconds(estimatedTotalSeconds)}</span>
                <span className="font-medium text-accent-600">Hang tight — almost there!</span>
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
                        <stop offset="0%" className="text-primary-600" stopColor="currentColor" />
                        <stop offset="100%" className="text-accent-500" stopColor="currentColor" />
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

              <div className="relative overflow-hidden rounded-2xl border border-indigo-100/80 bg-white/60 p-6">
                {showAuthPrompt && (
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-b from-white/30 via-white/60 to-white/90 backdrop-blur-[2px]" />
                )}
                <div
                  className={`relative ${showAuthPrompt ? 'select-none text-gray-600/90 blur-[1.5px]' : ''}`}
                  aria-hidden={showAuthPrompt}
                >
                  <h4 className="mb-2 font-semibold text-gray-900">Executive Summary</h4>
                  <p>{result.summary}</p>
                </div>
                {showAuthPrompt && (
                  <div className="relative z-20 mt-6 flex justify-end">
                    <AuthPromptCard
                      onSelectMode={openAuthModal}
                      statusMessage={promptStatusMessage}
                      errorMessage={promptErrorMessage}
                      disabled={promptDisabled}
                      showSignOut={Boolean(authToken)}
                      onSignOut={authToken ? handleSignOut : undefined}
                    />
                  </div>
                )}
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

            <div className="relative overflow-hidden rounded-2xl border border-primary-100/60 bg-white p-8 shadow-xl">
              {showAuthPrompt && (
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-b from-white/40 via-white/75 to-white/95 backdrop-blur-[3px]" />
              )}
              <div
                className={`relative ${showAuthPrompt ? 'select-none text-gray-600/90 blur-[2px]' : ''}`}
                aria-hidden={showAuthPrompt}
              >
                <h4 className="mb-4 font-semibold text-gray-900">Detailed Analysis</h4>
                {result.pages.map((page, idx) => (
                  <div key={idx} className="mb-6">
                    <h5 className="mb-2 font-medium text-gray-700">{page.title}</h5>
                    <p>{page.feedback}</p>
                  </div>
                ))}
              </div>
              {showAuthPrompt && (
                <div className="relative z-20 mt-6 flex justify-end">
                  <AuthPromptCard
                    onSelectMode={openAuthModal}
                    statusMessage={promptStatusMessage}
                    errorMessage={promptErrorMessage}
                    disabled={promptDisabled}
                    showSignOut={Boolean(authToken)}
                    onSignOut={authToken ? handleSignOut : undefined}
                  />
                </div>
              )}
            </div>

            {/* Membership Value */}
            <div className="mt-10 rounded-3xl border border-primary-100 bg-gradient-to-br from-white via-primary-50/70 to-accent-50/60 p-8 shadow-lg">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <h3 className="text-2xl font-bold text-gray-900">Everything you unlock with Pro</h3>
                  <p className="mt-2 text-sm text-gray-600">
                    Free scans cover your first page. Funnel Analyzer Pro unlocks multi-step funnels, unlimited analyses, and deeper conversion playbooks.
                  </p>
                </div>
                <div className="text-left sm:text-right text-xs font-semibold uppercase tracking-[0.35em] text-accent-600">
                  Pro Advantage
                </div>
              </div>
              <div className="mt-6 grid gap-5 md:grid-cols-2">
                {UPGRADE_FEATURES.map((feature) => (
                  <div key={feature.title} className="rounded-2xl border border-white/70 bg-white/80 p-5 shadow-sm">
                    <h4 className="text-base font-semibold text-gray-900">{feature.title}</h4>
                    <p className="mt-2 text-sm text-gray-600">{feature.description}</p>
                  </div>
                ))}
              </div>
              <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center">
                <a
                  href={FUNNEL_ANALYZER_JOIN_URL}
                  className="inline-flex items-center justify-center rounded-xl bg-gradient-to-r from-primary-600 to-accent-500 px-6 py-3 text-sm font-semibold text-white shadow-lg transition-all hover:from-primary-700 hover:to-accent-600"
                >
                  Upgrade to Funnel Analyzer Pro
                </a>
                <Link
                  href="/pricing"
                  className="inline-flex items-center justify-center rounded-xl border border-primary-200 px-6 py-3 text-sm font-semibold text-primary-600 transition-colors hover:border-primary-300 hover:text-primary-700"
                >
                  See plan comparison
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </main>
      <AuthModal
        open={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        defaultMode={authModalMode}
      />
    </div>
  );
}
