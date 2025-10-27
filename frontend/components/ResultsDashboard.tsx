'use client'

import { useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { FiDownload, FiRefreshCw } from 'react-icons/fi'
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'
import ScoreCard from '@/components/ScoreCard'
import PageAnalysisCard from '@/components/PageAnalysisCard'
import { AnalysisResult } from '@/types'

interface Props {
  analysis: AnalysisResult
}

export default function ResultsDashboard({ analysis }: Props) {
  const reportRef = useRef<HTMLDivElement | null>(null)
  const [isExporting, setIsExporting] = useState(false)

  const handleNewAnalysis = () => {
    window.location.reload()
  }

  const handleExportPDF = async () => {
    if (!reportRef.current || isExporting) return

    setIsExporting(true)
    try {
      const element = reportRef.current
      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        windowWidth: element.scrollWidth,
        windowHeight: element.scrollHeight,
      })

      const imgData = canvas.toDataURL('image/png')
      const pdf = new jsPDF('p', 'mm', 'a4')
      const pdfWidth = pdf.internal.pageSize.getWidth()
      const pdfHeight = pdf.internal.pageSize.getHeight()
      const imgProps = pdf.getImageProperties(imgData)
      const imgHeight = (imgProps.height * pdfWidth) / imgProps.width
      let heightLeft = imgHeight
      let position = 0

      pdf.addImage(imgData, 'PNG', 0, position, pdfWidth, imgHeight)
      heightLeft -= pdfHeight

      while (heightLeft > 0) {
        position = heightLeft - imgHeight
        pdf.addPage()
        pdf.addImage(imgData, 'PNG', 0, position, pdfWidth, imgHeight)
        heightLeft -= pdfHeight
      }

      pdf.save(`funnel-analysis-${analysis.overall_score}.pdf`)
    } catch (error) {
      console.error('Failed to export PDF', error)
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <motion.div
      ref={reportRef}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header with Actions */}
      <div className="flex justify-between items-center mb-8">
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

      {/* Summary */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white rounded-xl shadow-soft p-6 mb-8"
      >
        <h2 className="text-xl font-semibold text-slate-900 mb-3">
          Executive Summary
        </h2>
        <p className="text-slate-700 leading-relaxed">
          {analysis.summary}
        </p>
      </motion.div>

      {/* Individual Page Analyses */}
      <div className="space-y-6">
        <h2 className="text-xl font-semibold text-slate-900">
          Page-by-Page Analysis
        </h2>
        {analysis.pages.map((page, index) => (
          <PageAnalysisCard key={index} page={page} index={index} />
        ))}
      </div>
    </motion.div>
  )
}
