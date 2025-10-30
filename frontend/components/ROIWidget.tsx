'use client'

import { motion } from 'framer-motion'
import { FiTrendingUp, FiZap, FiDollarSign } from 'react-icons/fi'

interface ROIWidgetProps {
  potentialGain: number // Monthly revenue potential
  capturedSoFar: number // Revenue captured from completed fixes
  topFixes: Array<{
    title: string
    impact: number
  }>
  completionPercentage: number
}

export default function ROIWidget({ 
  potentialGain, 
  capturedSoFar, 
  topFixes,
  completionPercentage 
}: ROIWidgetProps) {
  const remaining = potentialGain - capturedSoFar

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-br from-emerald-50 to-teal-50 border-2 border-emerald-200 rounded-2xl p-6 shadow-lg"
    >
      <div className="flex items-center gap-3 mb-4">
        <div className="p-3 bg-emerald-500 rounded-xl">
          <FiDollarSign className="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-emerald-900">ROI Impact</h3>
          <p className="text-sm text-emerald-700">Monthly revenue potential</p>
        </div>
      </div>

      {/* Potential Gain */}
      <div className="bg-white rounded-xl p-4 mb-3 border border-emerald-100">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-slate-600">Potential Gain</span>
          <FiTrendingUp className="w-4 h-4 text-emerald-600" />
        </div>
        <div className="text-3xl font-bold text-emerald-600">
          +${potentialGain.toLocaleString()}/mo
        </div>
        <div className="text-xs text-slate-500 mt-1">
          Based on industry benchmarks
        </div>
      </div>

      {/* Captured So Far */}
      <div className="bg-white rounded-xl p-4 mb-3 border border-emerald-100">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-slate-600">Captured So Far</span>
          <span className="text-xs font-semibold text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full">
            {completionPercentage}% Complete
          </span>
        </div>
        <div className="text-2xl font-bold text-emerald-700">
          ${capturedSoFar.toLocaleString()}/mo
        </div>
        <div className="w-full bg-emerald-100 rounded-full h-2 mt-2">
          <div 
            className="bg-gradient-to-r from-emerald-500 to-teal-500 h-2 rounded-full transition-all duration-500"
            style={{ width: `${completionPercentage}%` }}
          />
        </div>
      </div>

      {/* Remaining */}
      <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-xl p-4 mb-4 border border-amber-200">
        <div className="flex items-center gap-2 mb-1">
          <FiZap className="w-4 h-4 text-amber-600" />
          <span className="text-sm font-semibold text-amber-900">Still Available</span>
        </div>
        <div className="text-xl font-bold text-amber-700">
          ${remaining.toLocaleString()}/mo
        </div>
      </div>

      {/* Top 3 Fixes */}
      <div className="space-y-2">
        <h4 className="text-sm font-bold text-slate-700 mb-3">Next Highest-Impact Fixes:</h4>
        {topFixes.slice(0, 3).map((fix, index) => (
          <div 
            key={index}
            className="bg-white rounded-lg p-3 border border-slate-200 hover:border-emerald-300 transition-colors"
          >
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-6 h-6 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center text-xs font-bold">
                {index + 1}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-slate-700 font-medium truncate">
                  {fix.title}
                </p>
                <p className="text-xs text-emerald-600 font-semibold mt-1">
                  +${fix.impact.toLocaleString()}/mo
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  )
}
