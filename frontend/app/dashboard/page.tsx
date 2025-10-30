'use client'

import { Suspense, useCallback, useEffect, useState } from 'react'
import { FiAlertTriangle, FiExternalLink, FiFileText, FiRefreshCw, FiTrash2 } from 'react-icons/fi'
import URLInputForm from '@/components/URLInputForm'
import ResultsDashboard from '@/components/ResultsDashboard'
import LoadingAnimation from '@/components/LoadingAnimation'
import { TopNav } from '@/components/TopNav'
import { useAnalysisStore } from '@/store/analysisStore'
import { useAuthValidation } from '@/hooks/useAuthValidation'
import { deleteReport, getReportDetail, getReports } from '@/lib/api'
import type { ReportListItem } from '@/types'

const DATE_OPTIONS: Intl.DateTimeFormatOptions = { dateStyle: 'medium', timeStyle: 'short' }
const PAGE_SIZE = 10

function formatTimestamp(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }
  return date.toLocaleString(undefined, DATE_OPTIONS)
}

function DashboardContent() {
  const {
    token,
    loading: authLoading,
    error: authError,
    authStatus,
    statusMessage,
    statusReason,
    portalUrl,
    accessGranted,
    isLocked,
    userId,
    auth,
  } = useAuthValidation()

  const currentAnalysis = useAnalysisStore((state) => state.currentAnalysis)
  const isAnalyzing = useAnalysisStore((state) => state.isAnalyzing)
  const setCurrentAnalysis = useAnalysisStore((state) => state.setCurrentAnalysis)

  const [reports, setReports] = useState<ReportListItem[]>([])
  const [reportsTotal, setReportsTotal] = useState(0)
  const [reportsLoading, setReportsLoading] = useState(false)
  const [reportsLoadingMore, setReportsLoadingMore] = useState(false)
  const [reportsError, setReportsError] = useState<string | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)
  const [viewingReportId, setViewingReportId] = useState<number | null>(null)
  const [deletingReportId, setDeletingReportId] = useState<number | null>(null)
  
  // Remove all modal interruptions - let users get to their analysis immediately
  // Password and profile setup can be done later in settings if needed

  const fetchReports = useCallback(
    async ({ offset = 0, append = false }: { offset?: number; append?: boolean } = {}) => {
    if (!userId) {
      setReports([])
      setReportsTotal(0)
      setReportsError(null)
      return
    }

      if (append) {
        setReportsLoadingMore(true)
      } else {
        setReportsLoading(true)
      }

      if (!append) {
        setReportsError(null)
      }
      setActionError(null)

      try {
        const response = await getReports(userId, PAGE_SIZE, offset)

        setReports((prev) => (append ? [...prev, ...response.reports] : response.reports))
        setReportsTotal(response.total)
      } catch (error: any) {
        const message = error?.message || 'Failed to fetch stored analyses.'
        if (append) {
          setActionError(message)
        } else {
          setReportsError(message)
        }
      } finally {
        if (append) {
          setReportsLoadingMore(false)
        } else {
          setReportsLoading(false)
        }
      }
    },
    [userId],
  )

  useEffect(() => {
    if (!userId) {
      setReports([])
      setReportsTotal(0)
      return
    }

    void fetchReports({ offset: 0, append: false })
  }, [userId, fetchReports])

  useEffect(() => {
    if (!userId || !currentAnalysis) {
      return
    }

    void fetchReports({ offset: 0, append: false })
  }, [userId, currentAnalysis, fetchReports])

  const handleViewReport = useCallback(async (analysisId: number) => {
    if (!userId) {
      return
    }

    setViewingReportId(analysisId)
    setActionError(null)
    try {
      const detail = await getReportDetail(analysisId, { userId })
      setCurrentAnalysis(detail)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } catch (error: any) {
      setActionError(error?.message || 'Failed to load report details.')
    } finally {
      setViewingReportId(null)
    }
  }, [userId, setCurrentAnalysis])

  const handleDeleteReport = useCallback(async (analysisId: number) => {
    if (!userId) {
      return
    }

    const confirmed = window.confirm('Delete this analysis and its stored screenshots?')
    if (!confirmed) {
      return
    }

    setDeletingReportId(analysisId)
    setActionError(null)
    try {
      await deleteReport(analysisId, { userId })
      setReports((prev) => prev.filter((report) => report.analysis_id !== analysisId))
      setReportsTotal((prev) => (prev > 0 ? prev - 1 : 0))
      if (currentAnalysis?.analysis_id === analysisId) {
        setCurrentAnalysis(null)
      }
    } catch (error: any) {
      setActionError(error?.message || 'Failed to delete report.')
    } finally {
      setDeletingReportId(null)
    }
  }, [userId, currentAnalysis, setCurrentAnalysis])

  const reportCount = reports.length

  const handleRefreshReports = useCallback(() => {
    if (!userId) {
      return
    }

    void fetchReports({ offset: 0, append: false })
  }, [userId, fetchReports])

  const handleLoadMore = useCallback(() => {
    if (!userId) {
      return
    }

    void fetchReports({ offset: reportCount, append: true })
  }, [userId, reportCount, fetchReports])

  const showMembershipAction = Boolean(token && !accessGranted && !authLoading && !authError)
  const hasReports = reportCount > 0
  const canLoadMore = reportCount < reportsTotal

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      <TopNav
        rightSlot={
          token ? (
            <span className="text-sm text-slate-600">
              {authLoading ? 'Validating membership…' : authStatus || 'Authenticated'}
            </span>
          ) : null
        }
        showLoginButton={false}
      />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {authError && (
          <div className="mb-6 rounded-xl border border-rose-200 bg-rose-50 p-4 text-rose-700">
            <div className="flex items-center gap-2 font-semibold">
              <FiAlertTriangle />
              <span>Membership validation failed</span>
            </div>
            <p className="mt-1 text-sm">{authError}</p>
          </div>
        )}

        {showMembershipAction && (
          <div className="mb-6 rounded-xl border border-amber-200 bg-amber-50 p-5 text-amber-900">
            <div className="flex items-center gap-2 font-semibold text-amber-800">
              <FiAlertTriangle />
              <span>Membership Action Required</span>
            </div>
            <p className="mt-2 text-sm leading-relaxed">
              {statusMessage || 'Your membership is not active. Please update your subscription to unlock analyses.'}
            </p>
            {statusReason && (
              <p className="mt-1 text-xs text-amber-700">{statusReason}</p>
            )}
            {portalUrl && (
              <a
                href={portalUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-3 inline-flex items-center gap-1 text-sm font-semibold text-amber-800 hover:text-amber-900"
              >
                Manage billing <FiExternalLink className="text-xs" />
              </a>
            )}
          </div>
        )}

        {actionError && (
          <div className="mb-6 rounded-xl border border-rose-200 bg-rose-50 p-4 text-rose-700">
            <div className="flex items-center gap-2 font-semibold">
              <FiAlertTriangle />
              <span>Report action failed</span>
            </div>
            <p className="mt-1 text-sm">{actionError}</p>
          </div>
        )}

        {isAnalyzing ? (
          <LoadingAnimation />
        ) : currentAnalysis ? (
          <ResultsDashboard analysis={currentAnalysis} />
        ) : (
          <div className="max-w-3xl mx-auto">
            <div className="text-center mb-12">
              <h1 className="text-4xl font-bold text-slate-900 mb-4">
                Analyze Your Funnel
              </h1>
              <p className="text-lg text-slate-600">
                Enter your funnel URLs below to get AI-powered insights
              </p>
            </div>
            <URLInputForm isLocked={isLocked} />
          </div>
        )}

        {userId && (
          <section className="mt-12">
            <div className="bg-white/90 backdrop-blur border border-slate-200 rounded-2xl p-6 shadow-soft">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                  <h2 className="text-xl font-semibold text-slate-900">Recent analyses</h2>
                  <p className="text-sm text-slate-500">
                    Stored reports tied to your membership. Total saved: {reportsTotal}.
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={handleRefreshReports}
                    disabled={reportsLoading || reportsLoadingMore}
                    className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium text-primary-600 hover:text-primary-700 disabled:text-slate-400"
                  >
                    <FiRefreshCw className={`text-base ${(reportsLoading || reportsLoadingMore) ? 'animate-spin' : ''}`} />
                    Refresh
                  </button>
                  {canLoadMore && (
                    <button
                      type="button"
                      onClick={handleLoadMore}
                      disabled={reportsLoadingMore}
                      className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium text-slate-600 hover:text-slate-700 disabled:text-slate-400"
                    >
                      {reportsLoadingMore ? 'Loading…' : 'Load more'}
                    </button>
                  )}
                </div>
              </div>

              {reportsError && (
                <div className="mt-4 rounded-lg border border-rose-200 bg-rose-50 p-4 text-rose-700 text-sm">
                  {reportsError}
                </div>
              )}

              {!reportsLoading && !hasReports && !reportsError && (
                <p className="mt-6 text-sm text-slate-500">
                  No stored analyses yet. Run a report while your membership is active and it will appear here.
                </p>
              )}

              {reportsLoading && (
                <p className="mt-6 text-sm text-slate-500">Loading saved analyses…</p>
              )}

              {hasReports && (
                <ul className="mt-6 space-y-4">
                  {reports.map((report) => {
                    const additionalPages = Math.max(report.urls.length - 1, 0)
                    const displayName = report.name || `Analysis #${report.analysis_id}`
                    const isRerun = report.parent_analysis_id !== null && report.parent_analysis_id !== undefined
                    
                    return (
                      <li
                        key={report.analysis_id}
                        className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md"
                      >
                        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <span className="text-3xl font-bold text-slate-900">{report.overall_score}</span>
                              <span className="text-sm text-slate-500">overall score</span>
                              {isRerun && (
                                <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded">
                                  Re-run
                                </span>
                              )}
                            </div>
                            <div className="mt-2 text-sm text-slate-600">
                              <div className="font-semibold text-slate-900 mb-1">
                                {displayName}
                              </div>
                              <div className="font-medium text-slate-600 truncate text-xs" title={report.urls[0]}>
                                {report.urls[0]}
                              </div>
                              {additionalPages > 0 && (
                                <div className="text-xs">{`+${additionalPages} more page${additionalPages > 1 ? 's' : ''}`}</div>
                              )}
                              <div className="text-xs text-slate-500 mt-1">
                                {formatTimestamp(report.created_at)}
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center gap-3">
                            <button
                              type="button"
                              onClick={() => handleViewReport(report.analysis_id)}
                              disabled={viewingReportId === report.analysis_id}
                              className="inline-flex items-center gap-2 rounded-lg border border-primary-200 px-4 py-2 text-sm font-medium text-primary-600 hover:text-primary-700 disabled:opacity-60"
                            >
                              {viewingReportId === report.analysis_id ? 'Opening…' : (
                                <>
                                  <FiFileText className="text-base" />
                                  View
                                </>
                              )}
                            </button>
                            <button
                              type="button"
                              onClick={() => handleDeleteReport(report.analysis_id)}
                              disabled={deletingReportId === report.analysis_id}
                              className="inline-flex items-center gap-2 rounded-lg border border-rose-200 px-4 py-2 text-sm font-medium text-rose-600 hover:text-rose-700 disabled:opacity-60"
                            >
                              {deletingReportId === report.analysis_id ? 'Deleting…' : (
                                <>
                                  <FiTrash2 className="text-base" />
                                  Delete
                                </>
                              )}
                            </button>
                          </div>
                        </div>
                      </li>
                    )
                  })}
                </ul>
              )}
            </div>
          </section>
        )}
      </main>
    </div>
  )
}

function DashboardFallback() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      <TopNav />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <p className="text-sm text-slate-500">Loading membership dashboard…</p>
      </main>
    </div>
  )
}

export default function Dashboard() {
  return (
    <Suspense fallback={<DashboardFallback />}>
      <DashboardContent />
    </Suspense>
  )
}
