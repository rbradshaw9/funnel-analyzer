'use client'

import URLInputForm from '@/components/URLInputForm'
import ResultsDashboard from '@/components/ResultsDashboard'
import LoadingAnimation from '@/components/LoadingAnimation'
import { useAnalysisStore } from '@/store/analysisStore'

export default function Embed() {
  const { currentAnalysis, isAnalyzing } = useAnalysisStore()

  // Iframe-optimized version - minimal chrome
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 p-4">
      <div className="max-w-5xl mx-auto">
        {isAnalyzing ? (
          <LoadingAnimation />
        ) : currentAnalysis ? (
          <ResultsDashboard analysis={currentAnalysis} />
        ) : (
          <URLInputForm />
        )}
      </div>
    </div>
  )
}
