'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { initiateRerun, analyzeFunnel } from '@/lib/api'

interface RerunAnalysisButtonProps {
  analysisId: number
  userId?: number
  userToken?: string | null
}

export default function RerunAnalysisButton({ analysisId, userId, userToken }: RerunAnalysisButtonProps) {
  const router = useRouter()
  const [isRunning, setIsRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleRerun = async () => {
    setIsRunning(true)
    setError(null)

    try {
      // Get the original analysis URLs
      const rerunInfo = await initiateRerun(analysisId, userId)
      
      if (!rerunInfo.urls || rerunInfo.urls.length === 0) {
        throw new Error('No URLs found for re-run')
      }

      // Start a new analysis with the same URLs and link to parent
      const result = await analyzeFunnel(rerunInfo.urls, {
        userId,
        token: userToken || undefined,
        industry: 'other', // Could be improved to save original industry
        parentAnalysisId: analysisId, // Link to parent for version tracking
        onProgress: (progress) => {
          console.log('Re-run progress:', progress)
        },
      })

      // Navigate to the new analysis
      router.push(`/reports/${result.analysis_id}`)
    } catch (err: any) {
      console.error('Re-run failed:', err)
      setError(err.message || 'Failed to re-run analysis')
      setIsRunning(false)
    }
  }

  return (
    <div>
      <button
        onClick={handleRerun}
        disabled={isRunning}
        className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isRunning ? (
          <>
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
            <span className="text-sm font-medium">Re-analyzing...</span>
          </>
        ) : (
          <>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            <span className="text-sm font-medium">Re-run Analysis</span>
          </>
        )}
      </button>
      
      {error && (
        <p className="text-sm text-red-600 mt-2">{error}</p>
      )}
      
      {isRunning && (
        <p className="text-sm text-slate-600 mt-2">
          This may take a few minutes. You&apos;ll be redirected when complete.
        </p>
      )}
    </div>
  )
}
