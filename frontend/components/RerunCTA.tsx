'use client'

import { motion } from 'framer-motion'
import { FiRefreshCw, FiClock } from 'react-icons/fi'
import { useRouter } from 'next/navigation'

interface RerunCTAProps {
  lastRunDate: Date | string
  urls: string[]
  position?: 'top' | 'bottom'
}

export default function RerunCTA({ lastRunDate, urls, position = 'top' }: RerunCTAProps) {
  const router = useRouter()
  
  const daysSinceRun = Math.floor(
    (new Date().getTime() - new Date(lastRunDate).getTime()) / (1000 * 60 * 60 * 24)
  )

  const handleRerun = () => {
    // Navigate to new analysis page with pre-filled URLs
    const urlsParam = urls.join(',')
    router.push(`/analysis/new?urls=${encodeURIComponent(urlsParam)}`)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: position === 'top' ? -20 : 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-2xl p-6 shadow-lg ${
        position === 'bottom' ? 'mt-8' : 'mb-8'
      }`}
    >
      <div className="flex items-center justify-between gap-6 flex-wrap">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <FiClock className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-bold text-blue-900">
              Ready for an Update?
            </h3>
          </div>
          <p className="text-blue-700">
            Last analysis was <span className="font-semibold">{daysSinceRun} day{daysSinceRun !== 1 ? 's' : ''} ago</span>.
            {daysSinceRun >= 7 && (
              <span className="ml-1">
                Let's see how your improvements have impacted your scores!
              </span>
            )}
            {daysSinceRun < 7 && (
              <span className="ml-1">
                Re-run analysis to see updated scores and new recommendations.
              </span>
            )}
          </p>
        </div>
        <button
          onClick={handleRerun}
          className="flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold rounded-xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
        >
          <FiRefreshCw className="w-5 h-5" />
          Re-run Analysis
        </button>
      </div>
    </motion.div>
  )
}
