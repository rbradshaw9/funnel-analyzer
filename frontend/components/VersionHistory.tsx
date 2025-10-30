'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { getAnalysisVersions, type AnalysisVersion } from '@/lib/api'
import { motion, AnimatePresence } from 'framer-motion'

interface VersionHistoryProps {
  analysisId: number
  currentScore: number
  userId?: number
}

export default function VersionHistory({ analysisId, currentScore, userId }: VersionHistoryProps) {
  const router = useRouter()
  const [versions, setVersions] = useState<AnalysisVersion[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (isOpen && versions.length === 0) {
      loadVersions()
    }
  }, [isOpen])

  const loadVersions = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await getAnalysisVersions(analysisId, userId)
      setVersions(response.versions)
    } catch (err: any) {
      setError(err.message || 'Failed to load versions')
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 65) return 'text-amber-600'
    return 'text-red-600'
  }

  const getScoreDelta = (currentVersion: AnalysisVersion, previousVersion?: AnalysisVersion) => {
    if (!previousVersion) return null
    const delta = currentVersion.overall_score - previousVersion.overall_score
    return delta
  }

  if (versions.length <= 1) {
    return null // Don't show if only one version
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
      >
        <svg className="w-5 h-5 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span className="text-sm font-medium text-slate-700">
          Version History ({versions.length || '?'})
        </span>
        <svg
          className={`w-4 h-4 text-slate-600 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-xl border border-slate-200 z-50 max-h-96 overflow-y-auto"
          >
            {loading && (
              <div className="p-6 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
                <p className="text-sm text-slate-600 mt-2">Loading versions...</p>
              </div>
            )}

            {error && (
              <div className="p-4 text-center text-red-600">
                <p className="text-sm">{error}</p>
              </div>
            )}

            {!loading && !error && versions.length > 0 && (
              <div className="p-2">
                <div className="px-3 py-2 border-b border-slate-200">
                  <h3 className="text-sm font-semibold text-slate-900">Analysis History</h3>
                  <p className="text-xs text-slate-600 mt-1">
                    Track improvements across {versions.length} version{versions.length > 1 ? 's' : ''}
                  </p>
                </div>

                <div className="py-2">
                  {versions.map((version, idx) => {
                    const previousVersion = versions[idx - 1]
                    const delta = getScoreDelta(version, previousVersion)
                    const isCurrent = version.is_current

                    return (
                      <button
                        key={version.analysis_id}
                        onClick={() => {
                          if (!isCurrent) {
                            router.push(`/reports/${version.analysis_id}`)
                          }
                          setIsOpen(false)
                        }}
                        className={`w-full px-3 py-3 hover:bg-slate-50 transition-colors text-left ${
                          isCurrent ? 'bg-primary-50 border-l-4 border-primary-500' : ''
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-medium text-slate-900">
                                {version.name || `Version ${version.version}`}
                              </span>
                              {isCurrent && (
                                <span className="px-2 py-0.5 bg-primary-100 text-primary-700 text-xs font-medium rounded">
                                  Current
                                </span>
                              )}
                            </div>
                            <p className="text-xs text-slate-600 mt-1">
                              {new Date(version.created_at).toLocaleDateString(undefined, {
                                month: 'short',
                                day: 'numeric',
                                year: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit',
                              })}
                            </p>
                          </div>

                          <div className="text-right">
                            <div className={`text-lg font-bold ${getScoreColor(version.overall_score)}`}>
                              {version.overall_score}
                            </div>
                            {delta !== null && (
                              <div className={`text-xs font-medium ${delta >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {delta >= 0 ? '+' : ''}{delta}
                              </div>
                            )}
                          </div>
                        </div>
                      </button>
                    )
                  })}
                </div>

                {versions.length > 1 && (
                  <div className="px-3 py-2 border-t border-slate-200 bg-slate-50">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-600">Score Progress:</span>
                      <span className={`font-semibold ${getScoreColor(versions[versions.length - 1].overall_score)}`}>
                        {versions[0].overall_score} → {versions[versions.length - 1].overall_score}
                        {' '}
                        <span className={versions[versions.length - 1].overall_score >= versions[0].overall_score ? 'text-green-600' : 'text-red-600'}>
                          ({versions[versions.length - 1].overall_score >= versions[0].overall_score ? '+' : ''}
                          {versions[versions.length - 1].overall_score - versions[0].overall_score})
                        </span>
                      </span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
