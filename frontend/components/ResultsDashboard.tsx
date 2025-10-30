'use client'

import { useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { FiDownload, FiRefreshCw } from 'react-icons/fi'
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'
import ScoreCard from '@/components/ScoreCard'
import PageAnalysisCard from '@/components/PageAnalysisCard'
import ActionableRecommendations from '@/components/ActionableRecommendations'
import { AnalysisResult } from '@/types'

interface Props {
  analysis: AnalysisResult
}

export default function ResultsDashboard({ analysis }: Props) {
  const reportRef = useRef<HTMLDivElement | null>(null)
  const [isExporting, setIsExporting] = useState(false)
  const [activeSection, setActiveSection] = useState('overview')

  const handleNewAnalysis = () => {
    window.location.reload()
  }
  
  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
      setActiveSection(sectionId)
    }
  }

  const handleExportPDF = async () => {
    if (!reportRef.current || isExporting) return

    setIsExporting(true)
    try {
      const element = reportRef.current
      
      // Higher quality settings for better PDF output
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

      // Add first page
      pdf.addImage(imgData, 'PNG', 0, position, pdfWidth, imgHeight, undefined, 'FAST')
      heightLeft -= pdfHeight

      // Add subsequent pages if needed
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
    <div className="flex gap-8 max-w-7xl mx-auto">
      {/* Navigation Sidebar */}
      <div className="hidden lg:block sticky top-8 h-fit w-64 flex-shrink-0">
        <div className="bg-white rounded-xl shadow-soft p-4">
          <h3 className="font-semibold text-slate-900 mb-4 text-sm">Report Navigation</h3>
          <nav className="space-y-2">
            {[
              { id: 'overview', label: 'Overview & Scores', icon: '📊' },
              { id: 'summary', label: 'Executive Summary', icon: '📋' },
              { id: 'pages', label: 'Page Analysis', icon: '🔍' },
              { id: 'recommendations', label: 'Recommendations', icon: '💡' },
            ].map((item) => (
              <button
                key={item.id}
                onClick={() => scrollToSection(item.id)}
                className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                  activeSection === item.id
                    ? 'bg-primary-100 text-primary-700 font-medium'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                <span className="mr-2">{item.icon}</span>
                {item.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Report Content */}
      <motion.div
        ref={reportRef}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="flex-1 min-w-0"
      >
      {/* Upgrade Banner for Limited Content */}
      {analysis.is_limited && analysis.upgrade_message && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 rounded-xl border-2 border-primary-200 bg-gradient-to-r from-primary-50 to-blue-50 p-5"
        >
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 mt-0.5">
              <svg className="h-6 w-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-slate-900 mb-1">
                Unlock Full Analysis
              </h3>
              <p className="text-slate-700 mb-3">{analysis.upgrade_message}</p>
              <button className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-primary-700">
                View Plans & Pricing
              </button>
            </div>
          </div>
        </motion.div>
      )}

      {/* Header with Actions */}
      <div id="overview" className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 mb-2">
            Funnel Analysis Report
          </h1>
          <p className="text-slate-600">
            Analyzed {analysis.pages.length} pages • 
            Overall Score: <span className="font-semibold text-primary-600">{analysis.overall_score}/100</span>
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleExportPDF}
            disabled={isExporting}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors disabled:cursor-not-allowed disabled:opacity-70"
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
          <button
            onClick={handleNewAnalysis}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <FiRefreshCw /> New Analysis
          </button>
        </div>
      </div>

      {/* Overall Score Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
        <ScoreCard label="Clarity" score={analysis.scores.clarity} />
        <ScoreCard label="Value" score={analysis.scores.value} />
        <ScoreCard label="Proof" score={analysis.scores.proof} />
        <ScoreCard label="Design" score={analysis.scores.design} />
        <ScoreCard label="Flow" score={analysis.scores.flow} />
      </div>

      {/* Executive Summary */}
      <motion.div
        id="summary"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white rounded-xl shadow-soft p-8 mb-8"
      >
        <h2 className="text-2xl font-bold text-slate-900 mb-6 flex items-center gap-2">
          <svg className="h-6 w-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          Executive Summary
        </h2>
        
        {/* Parse and format the summary into structured sections */}
        {analysis.summary.split(/\d+\.|\n\n|\. (?=[A-Z])/).filter(section => section.trim().length > 10).map((section, index) => {
          const trimmed = section.trim();
          if (!trimmed) return null;
          
          // Try to identify section types based on content
          const isOverview = index === 0 || trimmed.toLowerCase().includes('overall') || trimmed.toLowerCase().includes('performance');
          const isOpportunity = trimmed.toLowerCase().includes('opportunity') || trimmed.toLowerCase().includes('biggest') || trimmed.toLowerCase().includes('primary');
          const isRecommendation = trimmed.toLowerCase().includes('recommend') || trimmed.toLowerCase().includes('should') || trimmed.toLowerCase().includes('fix');
          const isStrength = trimmed.toLowerCase().includes('strength') || trimmed.toLowerCase().includes('working') || trimmed.toLowerCase().includes('good');
          
          let sectionTitle = 'Key Insight';
          let iconColor = 'text-slate-500';
          let bgColor = 'bg-slate-50';
          
          if (isOverview) {
            sectionTitle = 'Performance Overview';
            iconColor = 'text-blue-600';
            bgColor = 'bg-blue-50';
          } else if (isOpportunity) {
            sectionTitle = 'Primary Opportunity';
            iconColor = 'text-amber-600';
            bgColor = 'bg-amber-50';
          } else if (isRecommendation) {
            sectionTitle = 'Recommendations';
            iconColor = 'text-green-600';
            bgColor = 'bg-green-50';
          } else if (isStrength) {
            sectionTitle = 'Strengths';
            iconColor = 'text-emerald-600';
            bgColor = 'bg-emerald-50';
          }
          
          return (
            <div key={index} className={`mb-4 p-4 rounded-lg ${bgColor} border border-opacity-20`}>
              <h3 className={`text-sm font-semibold ${iconColor} mb-2 flex items-center gap-2`}>
                {isOverview && (
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                )}
                {isOpportunity && (
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                )}
                {isRecommendation && (
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                )}
                {isStrength && (
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                )}
                {sectionTitle}
              </h3>
              <p className="text-slate-700 leading-relaxed">{trimmed}</p>
            </div>
          );
        })}
        
        {/* Fallback if summary parsing doesn't work well */}
        {analysis.summary.split(/\d+\.|\n\n|\. (?=[A-Z])/).filter(section => section.trim().length > 10).length === 0 && (
          <div className="bg-slate-50 p-4 rounded-lg">
            <p className="text-slate-700 leading-relaxed">{analysis.summary}</p>
          </div>
        )}
      </motion.div>

      {/* Individual Page Analyses */}
      <div id="pages" className="space-y-6 mb-8">
        <h2 className="text-xl font-semibold text-slate-900">
          Page-by-Page Analysis
        </h2>
        {analysis.pages.map((page, index) => (
          <PageAnalysisCard key={index} page={page} index={index} />
        ))}
      </div>

      {/* Actionable Recommendations */}
      <div id="recommendations">
        <ActionableRecommendations analysis={analysis} />
      </div>
      </motion.div>
    </div>
  )
}
