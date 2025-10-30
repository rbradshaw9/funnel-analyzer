'use client'

import { useEffect, useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface AnalysisProgressModalProps {
  isOpen: boolean
  totalPages: number
  onComplete?: (analysisId: number) => void
  onError?: (error: string) => void
  analysisId?: string // UUID from backend for progress tracking
}

interface ProgressStage {
  percent: number
  message: string
  duration: number
}

export default function AnalysisProgressModal({
  isOpen,
  totalPages,
  onComplete,
  onError,
  analysisId,
}: AnalysisProgressModalProps) {
  const [progress, setProgress] = useState(0)
  const [progressMessage, setProgressMessage] = useState('')
  const [elapsedSeconds, setElapsedSeconds] = useState(0)
  const [currentPage, setCurrentPage] = useState(0)
  const progressIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const elapsedIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null)

  // Progress stages matching backend
  const progressStages: ProgressStage[] = [
    { percent: 10, message: 'Validating URLs and checking accessibility...', duration: 2 },
    { percent: 20, message: 'Extracting content from pages...', duration: 3 },
    { percent: 35, message: 'Capturing screenshots and analyzing visual elements...', duration: 5 },
    { percent: 55, message: 'Evaluating copy, design, and proof elements...', duration: 8 },
    { percent: 75, message: 'Analyzing conversion optimization opportunities...', duration: 6 },
    { percent: 90, message: 'Preparing executive summary and recommendations...', duration: 3 },
  ]

  useEffect(() => {
    if (!isOpen) {
      setProgress(0)
      setProgressMessage('')
      setElapsedSeconds(0)
      setCurrentPage(0)
      if (progressIntervalRef.current) clearInterval(progressIntervalRef.current)
      if (elapsedIntervalRef.current) clearInterval(elapsedIntervalRef.current)
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current)
      return
    }

    // Start elapsed time counter
    elapsedIntervalRef.current = setInterval(() => {
      setElapsedSeconds(prev => prev + 1)
    }, 1000)

    // Simulate progress through stages
    let currentStageIndex = 0
    let stageStartTime = Date.now()

    const updateProgress = () => {
      if (currentStageIndex >= progressStages.length) {
        return
      }

      const currentStage = progressStages[currentStageIndex]
      const elapsed = (Date.now() - stageStartTime) / 1000

      if (elapsed >= currentStage.duration) {
        currentStageIndex++
        stageStartTime = Date.now()
        
        if (currentStageIndex < progressStages.length) {
          const nextStage = progressStages[currentStageIndex]
          setProgress(nextStage.percent)
          setProgressMessage(nextStage.message)
        }
      } else {
        const stageProgress = elapsed / currentStage.duration
        if (currentStageIndex > 0) {
          const prevPercent = progressStages[currentStageIndex - 1].percent
          const currentPercent = currentStage.percent
          const interpolated = prevPercent + (currentPercent - prevPercent) * stageProgress
          setProgress(Math.round(interpolated))
        }
      }
    }

    setProgress(progressStages[0].percent)
    setProgressMessage(progressStages[0].message)

    progressIntervalRef.current = setInterval(updateProgress, 500)

    return () => {
      if (progressIntervalRef.current) clearInterval(progressIntervalRef.current)
      if (elapsedIntervalRef.current) clearInterval(elapsedIntervalRef.current)
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current)
    }
  }, [isOpen])

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full p-8"
        >
          <div className="text-center mb-6">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
              <svg className="w-8 h-8 text-primary-600 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2">Analyzing Your Funnel</h2>
            <p className="text-slate-600">
              AI-powered analysis in progress. This usually takes 15-45 seconds.
            </p>
          </div>

          <div className="bg-gradient-to-br from-slate-50 to-blue-50 rounded-lg p-6 border border-slate-200">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-medium text-slate-900">{progressMessage}</span>
              <div className="flex items-center gap-3">
                <span className="text-xs text-slate-500">{elapsedSeconds}s</span>
                <span className="text-sm font-bold text-primary-600">{progress}%</span>
              </div>
            </div>
            
            <div className="w-full bg-white rounded-full h-3 overflow-hidden shadow-inner border border-slate-200">
              <motion.div
                className="bg-gradient-to-r from-primary-500 via-primary-600 to-primary-500 h-3 rounded-full relative overflow-hidden"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5, ease: 'easeInOut' }}
              >
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                  animate={{ x: ['-100%', '200%'] }}
                  transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
                />
              </motion.div>
            </div>

            <div className="flex items-center justify-between mt-3">
              <p className="text-xs text-slate-600">
                Analyzing {totalPages} page{totalPages > 1 ? 's' : ''}
                {currentPage > 0 && ` • Currently on page ${currentPage}/${totalPages}`}
              </p>
              <p className="text-xs text-slate-500">
                Usually takes 15-45 seconds
              </p>
            </div>
          </div>

          <div className="mt-6 text-center">
            <p className="text-sm text-slate-500">
              🔍 Deep analysis includes: Copy effectiveness • Visual design • Trust elements • CTA optimization • Technical SEO
            </p>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}
