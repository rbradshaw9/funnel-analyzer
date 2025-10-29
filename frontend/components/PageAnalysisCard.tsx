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
  const hasInsights = Boolean(
    page.headline_recommendation ||
      (page.cta_recommendations && page.cta_recommendations.length > 0) ||
      (page.design_improvements && page.design_improvements.length > 0) ||
      (page.priority_alerts && page.priority_alerts.length > 0) ||
      (page.trust_elements_missing && page.trust_elements_missing.length > 0) ||
      page.ab_test_priority ||
      (page.video_recommendations && page.video_recommendations.length > 0) ||
      (page.email_capture_recommendations && page.email_capture_recommendations.length > 0) ||
      page.copy_diagnostics ||
      page.visual_diagnostics ||
      (page.funnel_flow_gaps && page.funnel_flow_gaps.length > 0)
  )

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
      {page.screenshot_url ? (
        <div className="relative mb-4 h-72 w-full overflow-hidden rounded-lg border border-slate-200 bg-slate-50">
          <Image
            src={page.screenshot_url}
            alt={`Screenshot of ${page.url}`}
            fill
            className="object-cover object-top"
            sizes="(max-width: 768px) 100vw, 50vw"
            priority={index === 0}
            onError={(e) => {
              console.error('Failed to load screenshot:', page.screenshot_url)
              console.log('Screenshot URL:', page.screenshot_url)
              // Show fallback message instead of hiding
              const container = e.currentTarget.parentElement
              if (container) {
                container.innerHTML = `
                  <div class="flex items-center justify-center h-72 bg-slate-100 rounded-lg border-2 border-dashed border-slate-300">
                    <div class="text-center">
                      <svg class="mx-auto h-12 w-12 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <p class="mt-2 text-sm text-slate-500">Screenshot not available</p>
                      <p class="text-xs text-slate-400">${page.url}</p>
                    </div>
                  </div>
                `
              }
            }}
          />
        </div>
      ) : (
        <div className="mb-4 h-72 w-full flex items-center justify-center bg-slate-100 rounded-lg border-2 border-dashed border-slate-300">
          <div className="text-center">
            <svg className="mx-auto h-12 w-12 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <p className="mt-2 text-sm text-slate-500">Screenshot capture in progress...</p>
            <p className="text-xs text-slate-400">Screenshots will appear when S3 storage is configured</p>
          </div>
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

      {hasInsights && (
        <div className="mt-4 space-y-4">
          {page.headline_recommendation && (
            <section className="bg-white border border-primary-100 rounded-lg p-4">
              <h5 className="text-sm font-semibold text-primary-700 mb-2">Headline Recommendation</h5>
              <p className="text-sm text-slate-800">{page.headline_recommendation}</p>
            </section>
          )}

          {page.ab_test_priority && (
            <section className="bg-white border border-amber-200 rounded-lg p-4">
              <h5 className="text-sm font-semibold text-amber-700 mb-2">A/B Test Priority</h5>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-slate-700">
                {page.ab_test_priority.element && (
                  <div><span className="font-semibold">Element:</span> {page.ab_test_priority.element}</div>
                )}
                {page.ab_test_priority.variant && (
                  <div><span className="font-semibold">Variant:</span> {page.ab_test_priority.variant}</div>
                )}
                {page.ab_test_priority.control && (
                  <div><span className="font-semibold">Control:</span> {page.ab_test_priority.control}</div>
                )}
                {page.ab_test_priority.expected_lift && (
                  <div><span className="font-semibold">Expected Lift:</span> {page.ab_test_priority.expected_lift}</div>
                )}
                {page.ab_test_priority.reasoning && (
                  <div className="md:col-span-2"><span className="font-semibold">Why:</span> {page.ab_test_priority.reasoning}</div>
                )}
              </div>
            </section>
          )}

          {page.priority_alerts && page.priority_alerts.length > 0 && (
            <section className="bg-rose-50 border border-rose-200 rounded-lg p-4">
              <h5 className="text-sm font-semibold text-rose-700 mb-3">Priority Alerts</h5>
              <ul className="space-y-2">
                {page.priority_alerts.map((alert, idx) => (
                  <li key={idx} className="text-sm text-rose-900">
                    <div className="font-semibold uppercase tracking-wide text-xs text-rose-600">
                      {alert.severity || 'Medium'} impact
                    </div>
                    <div className="font-semibold">{alert.issue}</div>
                    {alert.impact && <div className="text-rose-700">Impact: {alert.impact}</div>}
                    {alert.fix && <div className="text-rose-700">Fix: {alert.fix}</div>}
                  </li>
                ))}
              </ul>
            </section>
          )}

          {page.cta_recommendations && page.cta_recommendations.length > 0 && (
            <section className="bg-white border border-emerald-200 rounded-lg p-4">
              <h5 className="text-sm font-semibold text-emerald-700 mb-3">CTA Recommendations</h5>
              <ul className="space-y-2">
                {page.cta_recommendations.map((cta, idx) => (
                  <li key={idx} className="text-sm text-slate-800">
                    <div className="font-semibold">{cta.copy}</div>
                    <div className="text-slate-600 text-xs">
                      {[cta.location, cta.reason].filter(Boolean).join(' • ')}
                    </div>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {page.design_improvements && page.design_improvements.length > 0 && (
            <section className="bg-white border border-sky-200 rounded-lg p-4">
              <h5 className="text-sm font-semibold text-sky-700 mb-3">Design Improvements</h5>
              <ul className="space-y-2">
                {page.design_improvements.map((item, idx) => (
                  <li key={idx} className="text-sm text-slate-800">
                    <div className="font-semibold">{item.area || 'General'}</div>
                    <div>{item.recommendation}</div>
                    {item.impact && <div className="text-xs text-slate-600">Impact: {item.impact}</div>}
                  </li>
                ))}
              </ul>
            </section>
          )}

          {page.trust_elements_missing && page.trust_elements_missing.length > 0 && (
            <section className="bg-white border border-indigo-200 rounded-lg p-4">
              <h5 className="text-sm font-semibold text-indigo-700 mb-3">Trust Elements to Add</h5>
              <ul className="list-disc list-inside text-sm text-slate-800 space-y-1">
                {page.trust_elements_missing.map((item, idx) => (
                  <li key={idx}>
                    <span className="font-semibold">{item.element}</span>
                    {item.why && <span className="text-slate-600"> — {item.why}</span>}
                  </li>
                ))}
              </ul>
            </section>
          )}

          {page.funnel_flow_gaps && page.funnel_flow_gaps.length > 0 && (
            <section className="bg-white border border-purple-200 rounded-lg p-4">
              <h5 className="text-sm font-semibold text-purple-700 mb-3">Funnel Flow Gaps</h5>
              <ul className="space-y-2">
                {page.funnel_flow_gaps.map((gap, idx) => (
                  <li key={idx} className="text-sm text-slate-800">
                    <div className="font-semibold">{gap.step || 'Funnel Step'}</div>
                    <div>{gap.issue}</div>
                    {gap.fix && <div className="text-xs text-slate-600">Fix: {gap.fix}</div>}
                  </li>
                ))}
              </ul>
            </section>
          )}

          {(page.copy_diagnostics || page.visual_diagnostics) && (
            <section className="bg-slate-50 border border-slate-200 rounded-lg p-4">
              <h5 className="text-sm font-semibold text-slate-900 mb-3">Diagnostics</h5>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-slate-700">
                {page.copy_diagnostics && (
                  <div>
                    <h6 className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-2">Copy</h6>
                    <ul className="space-y-1">
                      {Object.entries(page.copy_diagnostics).map(([key, value]) => (
                        value ? (
                          <li key={key}><span className="font-semibold capitalize">{key}:</span> {value}</li>
                        ) : null
                      ))}
                    </ul>
                  </div>
                )}
                {page.visual_diagnostics && (
                  <div>
                    <h6 className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-2">Visual</h6>
                    <ul className="space-y-1">
                      {Object.entries(page.visual_diagnostics).map(([key, value]) => (
                        value ? (
                          <li key={key}><span className="font-semibold capitalize">{key}:</span> {value}</li>
                        ) : null
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </section>
          )}

          {page.video_recommendations && page.video_recommendations.length > 0 && (
            <section className="bg-white border border-slate-200 rounded-lg p-4">
              <h5 className="text-sm font-semibold text-slate-900 mb-3">Video Enhancements</h5>
              <ul className="list-disc list-inside text-sm text-slate-800 space-y-1">
                {page.video_recommendations.map((item, idx) => (
                  <li key={idx}>
                    <span className="font-semibold">{item.context || 'Placement'}:</span> {item.recommendation}
                  </li>
                ))}
              </ul>
            </section>
          )}

          {page.email_capture_recommendations && page.email_capture_recommendations.length > 0 && (
            <section className="bg-white border border-slate-200 rounded-lg p-4">
              <h5 className="text-sm font-semibold text-slate-900 mb-3">Email Capture & Nurture</h5>
              <ul className="list-disc list-inside text-sm text-slate-800 space-y-1">
                {page.email_capture_recommendations.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            </section>
          )}
        </div>
      )}
    </motion.div>
  )
}
