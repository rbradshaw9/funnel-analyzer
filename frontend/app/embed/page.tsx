'use client'

import { Suspense } from 'react'
import { FiAlertTriangle } from 'react-icons/fi'
import URLInputForm from '@/components/URLInputForm'
import ResultsDashboard from '@/components/ResultsDashboard'
import LoadingAnimation from '@/components/LoadingAnimation'
import { TopNav } from '@/components/TopNav'
import { useAnalysisStore } from '@/store/analysisStore'
import { useAuthValidation } from '@/hooks/useAuthValidation'
import { FUNNEL_ANALYZER_JOIN_URL } from '@/lib/externalLinks'

function EmbedContent() {
  const { currentAnalysis, isAnalyzing } = useAnalysisStore()
  const {
    token,
    loading: authLoading,
    error: authError,
    statusMessage,
    statusReason,
    accessGranted,
    isLocked,
  } = useAuthValidation()

  const showMembershipAction = Boolean(token && !accessGranted && !authLoading && !authError)

  // Iframe-optimized version - minimal chrome
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      <TopNav
        sticky={false}
        showLoginButton={false}
        rightSlot={
          token ? (
            <span className="text-sm text-slate-600">
              {authLoading ? 'Validating membership…' : authError ? 'Token error' : 'Membership embed'}
            </span>
          ) : (
            <a
              href={FUNNEL_ANALYZER_JOIN_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm font-semibold text-primary-600 hover:text-primary-700"
            >
              Funnel Analyzer Pro
            </a>
          )
        }
      />
      <div className="max-w-5xl mx-auto px-4 py-6">
        {token && authLoading && (
          <div className="mb-4 rounded-xl border border-blue-200 bg-blue-50 p-4 text-blue-800 text-sm">
            Validating membership…
          </div>
        )}

        {authError && (
          <div className="mb-4 rounded-xl border border-rose-200 bg-rose-50 p-4 text-rose-700 text-sm">
            <div className="flex items-center gap-2 font-semibold">
              <FiAlertTriangle className="text-base" />
              <span>Membership validation failed</span>
            </div>
            <p className="mt-1">{authError}</p>
          </div>
        )}

        {showMembershipAction && (
          <div className="mb-4 rounded-xl border border-amber-200 bg-amber-50 p-4 text-amber-900 text-sm">
            <div className="flex items-center gap-2 font-semibold text-amber-800">
              <FiAlertTriangle className="text-base" />
              <span>Membership Action Required</span>
            </div>
            <p className="mt-2">
              {statusMessage || 'Your membership is not active. Please update your subscription to unlock analyses.'}
            </p>
            {statusReason && (
              <p className="mt-1 text-xs text-amber-700">{statusReason}</p>
            )}
          </div>
        )}

        {isAnalyzing ? (
          <LoadingAnimation />
        ) : currentAnalysis ? (
          <ResultsDashboard analysis={currentAnalysis} />
        ) : (
          <URLInputForm isLocked={isLocked} />
        )}
      </div>
    </div>
  )
}

function EmbedFallback() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      <TopNav sticky={false} />
      <div className="max-w-5xl mx-auto px-4 py-6 text-sm text-slate-500">Loading embedded analyzer…</div>
    </div>
  )
}

export default function Embed() {
  return (
    <Suspense fallback={<EmbedFallback />}>
      <EmbedContent />
    </Suspense>
  )
}
