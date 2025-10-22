'use client'

import Image from 'next/image'
import { motion } from 'framer-motion'
import { FiExternalLink } from 'react-icons/fi'
import { PageAnalysis } from '@/types'

interface Props {
  page: PageAnalysis
  index: number
}

export default function PageAnalysisCard({ page, index }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="bg-white rounded-xl shadow-soft p-6"
    >
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="text-lg font-semibold text-slate-900">
              {page.title || `Page ${index + 1}`}
            </h3>
            {page.page_type && (
              <span className="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded-full font-medium">
                {page.page_type.replace('_', ' ')}
              </span>
            )}
          </div>
          <a
            href={page.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"
          >
            {page.url} <FiExternalLink className="text-xs" />
          </a>
        </div>
      </div>

      {/* Page Screenshot */}
      {page.screenshot_url && (
        <div className="relative mb-4 h-72 w-full overflow-hidden rounded-lg border border-slate-200">
          <Image
            src={page.screenshot_url}
            alt={`Screenshot of ${page.url}`}
            fill
            className="object-cover"
            sizes="(max-width: 768px) 100vw, 50vw"
            priority={index === 0}
          />
        </div>
      )}

      {/* Page Scores */}
      <div className="grid grid-cols-5 gap-2 mb-4">
        <div className="text-center p-2 bg-slate-50 rounded">
          <div className="text-xs text-slate-600 mb-1">Clarity</div>
          <div className="font-semibold">{page.scores.clarity}</div>
        </div>
        <div className="text-center p-2 bg-slate-50 rounded">
          <div className="text-xs text-slate-600 mb-1">Value</div>
          <div className="font-semibold">{page.scores.value}</div>
        </div>
        <div className="text-center p-2 bg-slate-50 rounded">
          <div className="text-xs text-slate-600 mb-1">Proof</div>
          <div className="font-semibold">{page.scores.proof}</div>
        </div>
        <div className="text-center p-2 bg-slate-50 rounded">
          <div className="text-xs text-slate-600 mb-1">Design</div>
          <div className="font-semibold">{page.scores.design}</div>
        </div>
        <div className="text-center p-2 bg-slate-50 rounded">
          <div className="text-xs text-slate-600 mb-1">Flow</div>
          <div className="font-semibold">{page.scores.flow}</div>
        </div>
      </div>

      {/* Page Feedback */}
      <div className="bg-slate-50 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-slate-900 mb-2">Analysis</h4>
        <p className="text-slate-700 text-sm leading-relaxed">{page.feedback}</p>
      </div>
    </motion.div>
  )
}
