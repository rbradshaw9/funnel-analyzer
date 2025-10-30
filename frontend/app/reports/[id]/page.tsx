'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { getReportDetail } from '@/lib/api'
import type { AnalysisResult } from '@/types'
import ResultsDashboard from '@/components/ResultsDashboard'
import LoadingAnimation from '@/components/LoadingAnimation'
import { TopNav } from '@/components/TopNav'
import EditableAnalysisName from '@/components/EditableAnalysisName'
import VersionHistory from '@/components/VersionHistory'
import RerunAnalysisButton from '@/components/RerunAnalysisButton'

export default function ReportPage() {
  const params = useParams()
  const router = useRouter()
  const [report, setReport] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadReport = async () => {
      try {
        setLoading(true)
        setError(null)
        
        const analysisId = parseInt(params.id as string, 10)
        if (isNaN(analysisId)) {
          setError('Invalid report ID')
          return
        }

        const data = await getReportDetail(analysisId)
        setReport(data)
      } catch (err: any) {
        console.error('Failed to load report:', err)
        setError(err.message || 'Failed to load report')
      } finally {
        setLoading(false)
      }
    }

    if (params.id) {
      void loadReport()
    }
  }, [params.id])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <TopNav />
      
      <main className="container mx-auto px-4 py-8">
        {loading && (
          <div className="flex flex-col items-center justify-center py-20">
            <LoadingAnimation />
            <p className="mt-4 text-slate-600">Loading your analysis report...</p>
          </div>
        )}

        {error && !loading && (
          <div className="max-w-2xl mx-auto">
            <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
              <svg className="mx-auto h-12 w-12 text-red-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <h2 className="text-xl font-semibold text-red-900 mb-2">Report Not Found</h2>
              <p className="text-red-700 mb-4">{error}</p>
              <button
                onClick={() => router.push('/dashboard')}
                className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Go to Dashboard
              </button>
            </div>
          </div>
        )}

        {report && !loading && (
          <div>
            <div className="mb-6">
              <button
                onClick={() => router.push('/dashboard')}
                className="text-primary-600 hover:text-primary-700 flex items-center gap-2 mb-4"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Back to Dashboard
              </button>
              
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <EditableAnalysisName
                    analysisId={report.analysis_id}
                    initialName={report.name}
                    onNameChange={(newName) => {
                      setReport({ ...report, name: newName })
                    }}
                  />
                  <p className="text-slate-600 mt-2">
                    Created on {new Date(report.created_at).toLocaleDateString(undefined, { 
                      dateStyle: 'long' 
                    })}
                  </p>
                </div>
                
                <div className="flex items-center gap-3">
                  <VersionHistory
                    analysisId={report.analysis_id}
                    currentScore={report.overall_score}
                  />
                  <RerunAnalysisButton
                    analysisId={report.analysis_id}
                  />
                </div>
              </div>
            </div>
            
            <ResultsDashboard analysis={report} />
          </div>
        )}
      </main>
    </div>
  )
}
