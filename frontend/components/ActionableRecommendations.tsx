'use client'

import { motion } from 'framer-motion'
import { FiCheckCircle, FiAlertTriangle, FiZap, FiTrendingUp, FiImage } from 'react-icons/fi'
import { AnalysisResult } from '@/types'
import Image from 'next/image'

interface ActionItem {
  priority: 'critical' | 'high' | 'medium' | 'low'
  category: string
  title: string
  description: string
  impact: string
  effort: 'Quick Win' | 'Medium Effort' | 'Major Project'
  steps: string[]
  pageUrl?: string
  screenshotUrl?: string
}

interface Props {
  analysis: AnalysisResult
}

export default function ActionableRecommendations({ analysis }: Props) {
  // Generate actionable items from the analysis
  const generateActionItems = (): ActionItem[] => {
    const items: ActionItem[] = []

    // Process each page's recommendations
    analysis.pages.forEach((page, pageIndex) => {
      const pageLabel = `Page ${pageIndex + 1}${page.title ? ` (${page.title})` : ''}`

      // Priority Alerts (Critical)
      if (page.priority_alerts && page.priority_alerts.length > 0) {
        page.priority_alerts.forEach(alert => {
          const severity = alert.severity?.toLowerCase() || 'medium'
          const priority = severity === 'high' || severity === 'critical' ? 'critical' : 
                          severity === 'medium' ? 'high' : 'medium'
          
          items.push({
            priority,
            category: 'Critical Issue',
            title: alert.issue,
            description: alert.impact || 'This issue may be hurting your conversion rates',
            impact: alert.impact || 'Potential conversion loss',
            effort: 'Quick Win',
            steps: alert.fix ? [alert.fix] : ['Review and address this issue immediately'],
            pageUrl: page.url,
            screenshotUrl: page.screenshot_url
          })
        })
      }

      // Headline Optimization (High Priority)
      if (page.headline_recommendation) {
        items.push({
          priority: 'high',
          category: 'Headline Optimization',
          title: `Improve ${pageLabel} Headline`,
          description: page.headline_recommendation,
          impact: 'Headlines are the first thing visitors see - can increase engagement by 20-30%',
          effort: 'Quick Win',
          steps: [
            'Draft 3-5 alternative headlines using the recommendation',
            'A/B test the new headline against current',
            'Measure click-through and scroll depth improvements',
            'Implement winning variation'
          ],
          pageUrl: page.url,
          screenshotUrl: page.screenshot_url
        })
      }

      // A/B Test Priorities (High)
      if (page.ab_test_priority) {
        const test = page.ab_test_priority
        items.push({
          priority: 'high',
          category: 'A/B Testing',
          title: `Test: ${test.element || 'Key Element'}`,
          description: test.reasoning || `Expected lift: ${test.expected_lift || 'Significant'}`,
          impact: `Potential ${test.expected_lift || '10-15%'} improvement`,
          effort: 'Medium Effort',
          steps: [
            `Current version: ${test.control || 'Existing'}`,
            `Test variant: ${test.variant || 'Recommended change'}`,
            'Set up A/B test with 50/50 traffic split',
            'Run for minimum 2 weeks or 1000 conversions',
            'Analyze results and implement winner'
          ],
          pageUrl: page.url,
          screenshotUrl: page.screenshot_url
        })
      }

      // Trust Elements (High Priority)
      if (page.trust_elements_missing && page.trust_elements_missing.length > 0) {
        items.push({
          priority: 'high',
          category: 'Trust Building',
          title: `Add Trust Elements to ${pageLabel}`,
          description: 'Missing credibility signals that build confidence',
          impact: 'Trust elements can increase conversion by 15-25%',
          effort: 'Medium Effort',
          steps: page.trust_elements_missing.map(elem => 
            `Add: ${elem.element}${elem.why ? ` - ${elem.why}` : ''}`
          ),
          pageUrl: page.url,
          screenshotUrl: page.screenshot_url
        })
      }

      // CTA Improvements (High)
      if (page.cta_recommendations && page.cta_recommendations.length > 0) {
        items.push({
          priority: 'high',
          category: 'Call-to-Action',
          title: `Optimize CTAs on ${pageLabel}`,
          description: 'Strategic CTA placement and copy improvements',
          impact: 'Better CTAs can boost conversions by 20-40%',
          effort: 'Quick Win',
          steps: page.cta_recommendations.map(cta => 
            `${cta.location ? `${cta.location}: ` : ''}"${cta.copy}"${cta.reason ? ` - ${cta.reason}` : ''}`
          ),
          pageUrl: page.url,
          screenshotUrl: page.screenshot_url
        })
      }

      // Design Improvements (Medium)
      if (page.design_improvements && page.design_improvements.length > 0) {
        items.push({
          priority: 'medium',
          category: 'Visual Design',
          title: `Design Enhancements for ${pageLabel}`,
          description: 'Visual improvements to increase engagement',
          impact: page.design_improvements[0]?.impact || 'Better visual hierarchy improves user experience',
          effort: 'Medium Effort',
          steps: page.design_improvements.map(improvement => 
            `${improvement.area ? `${improvement.area}: ` : ''}${improvement.recommendation}`
          ),
          pageUrl: page.url,
          screenshotUrl: page.screenshot_url
        })
      }

      // Funnel Flow Gaps (High)
      if (page.funnel_flow_gaps && page.funnel_flow_gaps.length > 0) {
        items.push({
          priority: 'high',
          category: 'Funnel Flow',
          title: `Fix Flow Issues on ${pageLabel}`,
          description: 'Critical gaps in your funnel journey',
          impact: 'Smooth funnel flow reduces drop-off by 25-35%',
          effort: 'Medium Effort',
          steps: page.funnel_flow_gaps.map(gap => 
            `${gap.step ? `${gap.step}: ` : ''}${gap.issue}${gap.fix ? ` → ${gap.fix}` : ''}`
          ),
          pageUrl: page.url,
          screenshotUrl: page.screenshot_url
        })
      }

      // Copy Diagnostics (Medium)
      if (page.copy_diagnostics) {
        const diag = page.copy_diagnostics
        const copyIssues = []
        if (diag.hook) copyIssues.push(`Hook: ${diag.hook}`)
        if (diag.offer) copyIssues.push(`Offer: ${diag.offer}`)
        if (diag.urgency) copyIssues.push(`Urgency: ${diag.urgency}`)
        if (diag.objections) copyIssues.push(`Objections: ${diag.objections}`)
        
        if (copyIssues.length > 0) {
          items.push({
            priority: 'medium',
            category: 'Copywriting',
            title: `Improve Copy on ${pageLabel}`,
            description: 'Strengthen your messaging and value proposition',
            impact: 'Better copy directly impacts conversion rates',
            effort: 'Medium Effort',
            steps: copyIssues,
            pageUrl: page.url,
            screenshotUrl: page.screenshot_url
          })
        }
      }

      // Video Recommendations (Medium)
      if (page.video_recommendations && page.video_recommendations.length > 0) {
        items.push({
          priority: 'medium',
          category: 'Video Content',
          title: `Add Video Content to ${pageLabel}`,
          description: 'Video can significantly boost engagement',
          impact: 'Video on landing pages can increase conversions by 80%',
          effort: 'Major Project',
          steps: page.video_recommendations.map(video => 
            `${video.context ? `${video.context}: ` : ''}${video.recommendation}`
          ),
          pageUrl: page.url,
          screenshotUrl: page.screenshot_url
        })
      }

      // Performance Optimization (Medium)
      if (page.performance_data && page.performance_data.performance_score && page.performance_data.performance_score < 70) {
        const opportunities = page.performance_data.opportunities || []
        if (opportunities.length > 0) {
          items.push({
            priority: 'medium',
            category: 'Page Speed',
            title: `Optimize Performance for ${pageLabel}`,
            description: `Current score: ${page.performance_data.performance_score}/100`,
            impact: '1 second delay can reduce conversions by 7%',
            effort: 'Medium Effort',
            steps: opportunities.slice(0, 5),
            pageUrl: page.url,
            screenshotUrl: page.screenshot_url
          })
        }
      }
    })

    // Sort by priority
    const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 }
    return items.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority])
  }

  const actionItems = generateActionItems()

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-300'
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-300'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      default:
        return 'bg-blue-100 text-blue-800 border-blue-300'
    }
  }

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'critical':
        return <FiAlertTriangle className="w-5 h-5" />
      case 'high':
        return <FiZap className="w-5 h-5" />
      case 'medium':
        return <FiTrendingUp className="w-5 h-5" />
      default:
        return <FiCheckCircle className="w-5 h-5" />
    }
  }

  const getEffortColor = (effort: string) => {
    switch (effort) {
      case 'Quick Win':
        return 'bg-green-100 text-green-800'
      case 'Medium Effort':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-purple-100 text-purple-800'
    }
  }

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-primary-50 to-blue-50 rounded-xl p-6 border border-primary-200">
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Your Action Plan</h2>
        <p className="text-slate-700 mb-4">
          We&apos;ve identified {actionItems.length} specific improvements you can make to increase conversions.
          Start with the highest priority items for maximum impact.
        </p>
        <div className="flex gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <span className="text-slate-600">Critical ({actionItems.filter(i => i.priority === 'critical').length})</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
            <span className="text-slate-600">High ({actionItems.filter(i => i.priority === 'high').length})</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <span className="text-slate-600">Medium ({actionItems.filter(i => i.priority === 'medium').length})</span>
          </div>
        </div>
      </div>

      {actionItems.map((item, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.05 }}
          className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden hover:shadow-md transition-shadow"
        >
          <div className="p-6">
            <div className="flex items-start gap-6 mb-4">
              {/* Screenshot Thumbnail */}
              {item.screenshotUrl && (
                <div className="flex-shrink-0">
                  <div className="relative w-32 h-24 rounded-lg overflow-hidden border border-slate-200 shadow-sm group">
                    <Image
                      src={item.screenshotUrl}
                      alt={`Screenshot of ${item.pageUrl || 'page'}`}
                      fill
                      className="object-cover object-top"
                      sizes="128px"
                    />
                    <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all flex items-center justify-center">
                      <FiImage className="w-6 h-6 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                  </div>
                  {item.pageUrl && (
                    <p className="text-xs text-slate-500 mt-1 truncate max-w-[128px]" title={item.pageUrl}>
                      {new URL(item.pageUrl).pathname || '/'}
                    </p>
                  )}
                </div>
              )}
              
              {/* Content */}
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold border flex items-center gap-1.5 ${getPriorityColor(item.priority)}`}>
                    {getPriorityIcon(item.priority)}
                    {item.priority.toUpperCase()}
                  </span>
                  <span className="px-3 py-1 bg-slate-100 text-slate-700 rounded-full text-xs font-medium">
                    {item.category}
                  </span>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${getEffortColor(item.effort)}`}>
                    {item.effort}
                  </span>
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">{item.title}</h3>
                <p className="text-slate-600 mb-3">{item.description}</p>
                <div className="bg-blue-50 border-l-4 border-blue-500 p-3 rounded">
                  <p className="text-sm font-semibold text-blue-900 flex items-center gap-2">
                    <FiTrendingUp className="w-4 h-4" />
                    Expected Impact: {item.impact}
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-4">
              <h4 className="text-sm font-semibold text-slate-900 mb-3 flex items-center gap-2">
                <FiCheckCircle className="w-4 h-4 text-primary-600" />
                Action Steps:
              </h4>
              <ol className="space-y-2">
                {item.steps.map((step, stepIndex) => (
                  <li key={stepIndex} className="flex items-start gap-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-xs font-semibold mt-0.5">
                      {stepIndex + 1}
                    </span>
                    <span className="text-sm text-slate-700 flex-1">{step}</span>
                  </li>
                ))}
              </ol>
            </div>
          </div>
        </motion.div>
      ))}

      {actionItems.length === 0 && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-8 text-center">
          <FiCheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-green-900 mb-2">Excellent Work!</h3>
          <p className="text-green-700">
            Your funnel is performing well. Continue monitoring and testing small improvements.
          </p>
        </div>
      )}
    </div>
  )
}
