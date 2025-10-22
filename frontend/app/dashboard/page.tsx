'use client'

import { useEffect, useState } from 'react'
import { FiBarChart2 } from 'react-icons/fi'
import URLInputForm from '@/components/URLInputForm'
import ResultsDashboard from '@/components/ResultsDashboard'
import LoadingAnimation from '@/components/LoadingAnimation'
import { useAnalysisStore } from '@/store/analysisStore'

export default function Dashboard() {
  const [token, setToken] = useState<string | null>(null)
  
  useEffect(() => {
    if (typeof window === 'undefined') return
    const params = new URLSearchParams(window.location.search)
    setToken(params.get('token'))
  }, [])
  
  const { currentAnalysis, isAnalyzing } = useAnalysisStore()

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      {/* Navigation */}
      <nav className="border-b border-slate-200 bg-white/80 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <FiBarChart2 className="text-primary-600 text-2xl" />
              <span className="text-xl font-semibold text-slate-900">Funnel Analyzer Pro</span>
            </div>
            <div className="flex items-center space-x-4">
              {token && (
                <span className="text-sm text-slate-600">
                  Authenticated
                </span>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
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
            <URLInputForm />
          </div>
        )}
      </main>
    </div>
  )
}
