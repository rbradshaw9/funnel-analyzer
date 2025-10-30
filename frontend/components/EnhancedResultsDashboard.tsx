'use client'

import { useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { FiDownload, FiRefreshCw, FiFileText, FiList, FiCheckSquare, FiClock } from 'react-icons/fi'
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'
import ScoreCard from '@/components/ScoreCard'
import PageAnalysisCard from '@/components/PageAnalysisCard'
import ActionableRecommendations from '@/components/ActionableRecommendations'
import ROIWidget from '@/components/ROIWidget'
import ScoreComparisonChart from '@/components/ScoreComparisonChart'
import StickyNavigation from '@/components/StickyNavigation'
import CollapsibleSection from '@/components/CollapsibleSection'
import RerunCTA from '@/components/RerunCTA'
import { AnalysisResult } from '@/types'

interface Props {
  analysis: AnalysisResult
}

export default function EnhancedResultsDashboard({ analysis }: Props) {
  const reportRef = useRef<HTMLDivElement | null>(null)
  const [isExporting, setIsExporting] = useState(false)

  // Calculate ROI metrics (simple estimation based on scores)
  const calculateROI = () => {
    const avgScore = analysis.overall_score
    const potentialGain = Math.round((100 - avgScore) * 50) // $50 per point improvement
    // For now, use a fixed completion percentage - this could come from the API later
    const completionPercentage = 35
    const captured = Math.round((completionPercentage / 100) * potentialGain)
    
    return {
      potentialGain,
      capturedSoFar: captured,
      completionPercentage,
      topFixes: [
        { title: 'Optimize headline for clarity', impact: 420 },
        { title: 'Add trust badges above fold', impact: 350 },
        { title: 'Improve CTA positioning', impact: 280 },
      ]
    }
  }

  const roi = calculateROI()

  // Navigation sections
  const navSections = [
    { id: 'overview', label: 'Overview', icon: FiFileText, completionBadge: undefined },
    { id: 'pages', label: 'Page Analysis', icon: FiList, completionBadge: analysis.pages.length },
    { id: 'recommendations', label: 'Action Plan', icon: FiCheckSquare, completionBadge: undefined },
    { id: 'history', label: 'History', icon: FiClock, completionBadge: undefined },
  ]

  const handleExportPDF = async () => {
    if (!reportRef.current || isExporting) return

    setIsExporting(true)
    try {
      const element = reportRef.current
      
      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        allowTaint: true,
        logging: false,
        windowWidth: element.scrollWidth,
        windowHeight: element.scrollHeight,
        backgroundColor: '#ffffff',
      })

      const imgData = canvas.toDataURL('image/png', 1.0)
      const pdf = new jsPDF('p', 'mm', 'a4')
      const pdfWidth = pdf.internal.pageSize.getWidth()
      const pdfHeight = pdf.internal.pageSize.getHeight()
      const imgProps = pdf.getImageProperties(imgData)
      const imgHeight = (imgProps.height * pdfWidth) / imgProps.width
      let heightLeft = imgHeight
      let position = 0

      pdf.addImage(imgData, 'PNG', 0, position, pdfWidth, imgHeight, undefined, 'FAST')
      heightLeft -= pdfHeight

      while (heightLeft > 0) {
        position = heightLeft - imgHeight
        pdf.addPage()
        pdf.addImage(imgData, 'PNG', 0, position, pdfWidth, imgHeight, undefined, 'FAST')
        heightLeft -= pdfHeight
      }

      const filename = `funnel-analysis-${analysis.overall_score}-${new Date().toISOString().split('T')[0]}.pdf`
      pdf.save(filename)
    } catch (error) {
      console.error('Failed to export PDF', error)
      alert('PDF export failed. Please try again or take a screenshot instead.')
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <>
      {/* Sticky Navigation */}
      <StickyNavigation 
        sections={navSections} 
        completionPercentage={roi.completionPercentage} 
      />

      {/* Main Content */}
      <motion.div
        ref={reportRef}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="max-w-7xl mx-auto"
      >
        {/* Re-run CTA at Top */}
        <RerunCTA 
          lastRunDate={analysis.created_at} 
          urls={analysis.urls || []}
          position="top"
        />

        {/* Header Section with ROI Widget */}
        <div id="overview" className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Left: Header */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h1 className="text-4xl font-bold text-slate-900 mb-2">
                    Funnel Analysis Report
                  </h1>
                  <p className="text-slate-600 text-lg">
                    Analyzed {analysis.pages.length} page{analysis.pages.length !== 1 ? 's' : ''} • 
                    <span className="font-semibold text-emerald-600 ml-2">
                      Score: {analysis.overall_score}/100
                    </span>
                  </p>
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={handleExportPDF}
                    disabled={isExporting}
                    className="flex items-center gap-2 px-4 py-2 bg-white border-2 border-slate-300 text-slate-700 rounded-xl hover:bg-slate-50 transition-all disabled:cursor-not-allowed disabled:opacity-70"
                  >
                    {isExporting ? (
                      <>
                        <FiRefreshCw className="animate-spin" /> Exporting...
                      </>
                    ) : (
                      <>
                        <FiDownload /> Export PDF
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Score Cards */}
              <div className="grid grid-cols-5 gap-4">
                <ScoreCard label="Clarity" score={analysis.scores.clarity} />
                <ScoreCard label="Value" score={analysis.scores.value} />
                <ScoreCard label="Proof" score={analysis.scores.proof} />
                <ScoreCard label="Design" score={analysis.scores.design} />
                <ScoreCard label="Flow" score={analysis.scores.flow} />
              </div>
            </div>
          </div>

          {/* Right: ROI Widget */}
          <div>
            <ROIWidget
              potentialGain={roi.potentialGain}
              capturedSoFar={roi.capturedSoFar}
              topFixes={roi.topFixes}
              completionPercentage={roi.completionPercentage}
            />
          </div>
        </div>

        {/* Score Comparison Chart */}
        <div className="mb-8">
          <ScoreComparisonChart
            currentScores={analysis.scores}
            previousScores={null} // TODO: Fetch previous report data
          />
        </div>

        {/* Executive Summary - Collapsible */}
        <div className="mb-8">
          <CollapsibleSection
            id="summary"
            title="Executive Summary"
            icon={FiFileText}
            defaultOpen={true}
          >
            <div className="mt-4 prose prose-slate max-w-none">
              <p className="text-slate-700 leading-relaxed text-lg">
                {analysis.summary}
              </p>
            </div>
          </CollapsibleSection>
        </div>

        {/* Page-by-Page Analysis - Collapsible */}
        <div id="pages" className="mb-8">
          <CollapsibleSection
            id="page-analysis"
            title="Page-by-Page Analysis"
            icon={FiList}
            badge={`${analysis.pages.length} ${analysis.pages.length === 1 ? 'Page' : 'Pages'}`}
            defaultOpen={true}
          >
            <div className="space-y-6 mt-6">
              {analysis.pages.map((page, index) => (
                <PageAnalysisCard key={index} page={page} index={index} />
              ))}
            </div>
          </CollapsibleSection>
        </div>

        {/* Action Plan / Recommendations - Collapsible */}
        <div id="recommendations" className="mb-8">
          <CollapsibleSection
            id="action-plan"
            title="Action Plan & Recommendations"
            icon={FiCheckSquare}
            defaultOpen={true}
          >
            <div className="mt-6">
              <ActionableRecommendations analysis={analysis} />
            </div>
          </CollapsibleSection>
        </div>

        {/* Re-run CTA at Bottom */}
        <RerunCTA 
          lastRunDate={analysis.created_at} 
          urls={analysis.urls || []}
          position="bottom"
        />
      </motion.div>
    </>
  )
}
