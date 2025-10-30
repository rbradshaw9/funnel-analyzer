'use client'

import { useMemo, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { FiDownload, FiRefreshCw, FiFileText, FiList, FiCheckSquare, FiClock, FiChevronRight, FiTrendingUp } from 'react-icons/fi'
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'
import ScoreCard from '@/components/ScoreCard'
import PageAnalysisCard from '@/components/PageAnalysisCard'
import ActionableRecommendations from '@/components/ActionableRecommendations'
import ScoreComparisonChart from '@/components/ScoreComparisonChart'
import StickyNavigation from '@/components/StickyNavigation'
import CollapsibleSection from '@/components/CollapsibleSection'
import RerunCTA from '@/components/RerunCTA'
import ROIPlanner from '@/components/ROIPlanner'
import { AnalysisResult } from '@/types'

interface Props {
  analysis: AnalysisResult
}

export default function EnhancedResultsDashboard({ analysis }: Props) {
  const reportRef = useRef<HTMLDivElement | null>(null)
  const [isExporting, setIsExporting] = useState(false)

  const generatedOn = useMemo(() => {
    try {
      return new Intl.DateTimeFormat('en-US', {
        month: 'long',
        day: 'numeric',
        year: 'numeric',
      }).format(new Date(analysis.created_at))
    } catch (error) {
      return analysis.created_at
    }
  }, [analysis.created_at])

  const humanDuration = useMemo(() => {
    if (!analysis.analysis_duration_seconds) return null
    const totalSeconds = analysis.analysis_duration_seconds
    const minutes = Math.floor(totalSeconds / 60)
    const seconds = Math.round(totalSeconds % 60)
    if (!minutes) return `${seconds}s turnaround`
    return `${minutes}m ${seconds}s turnaround`
  }, [analysis.analysis_duration_seconds])

  const summarySentences = useMemo(() => {
    const raw = analysis.summary || ''
    return raw
      .split(/\.(?=\s+[A-Z]|$)/)
      .map((sentence) => sentence.trim())
      .filter(Boolean)
  }, [analysis.summary])

  const primaryInsight = summarySentences[0] ?? 'We assessed your funnel experience and surfaced the most valuable opportunities to drive conversion lift.'
  const supportingInsights = summarySentences.slice(1, 4)

  const completionPercentage = useMemo(() => {
    return Math.min(100, Math.max(0, Math.round(analysis.overall_score)))
  }, [analysis.overall_score])

  const navSections = [
    { id: 'overview', label: 'Executive Overview', icon: FiFileText },
    { id: 'insights', label: 'Insights & ROI', icon: FiTrendingUp },
    { id: 'journey', label: 'Journey Diagnostics', icon: FiList, completionBadge: analysis.pages.length },
    { id: 'actions', label: 'Action Plan', icon: FiCheckSquare },
    { id: 'history', label: 'Momentum', icon: FiClock },
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

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id)
    if (!element) return
    const top = element.offsetTop - 96
    window.scrollTo({ top, behavior: 'smooth' })
  }

  return (
    <div className="relative">
      {/* Mobile floating navigator */}
      <div className="lg:hidden">
        <StickyNavigation sections={navSections} completionPercentage={completionPercentage} variant="floating" />
      </div>

      <motion.div
        ref={reportRef}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16"
      >
        <div className="lg:grid lg:grid-cols-[260px_1fr] lg:gap-10">
          <aside className="hidden lg:block">
            <StickyNavigation sections={navSections} completionPercentage={completionPercentage} variant="sidebar" />
          </aside>

          <div className="space-y-14">
            {/* Overview */}
            <section id="overview" className="scroll-mt-32">
              <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-slate-100">
                <div className="absolute inset-0 opacity-40" aria-hidden>
                  <div className="absolute -left-32 top-10 h-64 w-64 rounded-full bg-emerald-400/30 blur-3xl" />
                  <div className="absolute -right-40 bottom-0 h-72 w-72 rounded-full bg-sky-500/20 blur-3xl" />
                </div>
                <div className="relative z-10 flex flex-col gap-10 p-6 sm:p-10 lg:p-12">
                  <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
                    <div className="max-w-2xl space-y-3">
                      <span className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-white/80">
                        Analysis #{analysis.analysis_id}
                        <span className="h-1 w-1 rounded-full bg-emerald-400" />
                        {generatedOn}
                      </span>
                      <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
                        Funnel performance report
                      </h1>
                      <p className="text-sm text-white/70 sm:text-base">
                        We reviewed {analysis.pages.length} page{analysis.pages.length !== 1 ? 's' : ''} to uncover clarity, value, and flow opportunities that can unlock measurable growth.
                      </p>
                      <div className="flex flex-wrap gap-3 pt-3">
                        <button
                          onClick={() => scrollToSection('actions')}
                          className="inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm font-semibold text-slate-900 shadow-lg shadow-slate-900/20 transition hover:bg-slate-100"
                        >
                          View Action Plan
                          <FiChevronRight className="h-4 w-4" />
                        </button>
                        <button
                          onClick={handleExportPDF}
                          disabled={isExporting}
                          className="inline-flex items-center gap-2 rounded-full border border-white/30 bg-white/10 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/20 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          {isExporting ? (
                            <>
                              <FiRefreshCw className="h-4 w-4 animate-spin" /> Exporting…
                            </>
                          ) : (
                            <>
                              <FiDownload className="h-4 w-4" /> Export PDF
                            </>
                          )}
                        </button>
                      </div>
                    </div>

                    <div className="grid w-full gap-4 sm:grid-cols-2 lg:w-auto lg:grid-cols-1">
                      <div className="rounded-3xl border border-white/10 bg-white/10 p-5 backdrop-blur">
                        <p className="text-xs font-semibold uppercase tracking-wide text-white/60">Overall Score</p>
                        <p className="mt-3 text-5xl font-black text-white">{analysis.overall_score}</p>
                        <p className="text-xs text-white/60">/100 experience rating</p>
                      </div>
                      <div className="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                        <p className="text-xs font-semibold uppercase tracking-wide text-white/60">Pages audited</p>
                        <p className="mt-2 text-3xl font-bold text-white">{analysis.pages.length}</p>
                        <p className="text-xs text-white/60">Across your acquisition funnel</p>
                      </div>
                      {humanDuration && (
                        <div className="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                          <p className="text-xs font-semibold uppercase tracking-wide text-white/60">Processing time</p>
                          <p className="mt-2 text-lg font-semibold text-white">{humanDuration}</p>
                          <p className="text-xs text-white/60">From scrape to insight delivery</p>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur">
                    <h2 className="text-sm font-semibold uppercase tracking-[0.3em] text-white/60">Key Insight</h2>
                    <p className="mt-3 text-base text-white/90">
                      {primaryInsight}
                    </p>
                  </div>
                </div>
              </div>
            </section>

            {/* Insights & ROI */}
            <section id="insights" className="scroll-mt-32 space-y-10">
              <div className="grid gap-6 xl:grid-cols-[minmax(0,1.05fr)_minmax(0,0.95fr)]">
                <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-lg/20 shadow-slate-500/10 sm:p-8">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500">Highlights</p>
                      <h2 className="mt-2 text-2xl font-bold text-slate-900">What stood out in this review</h2>
                    </div>
                    <FiFileText className="h-6 w-6 text-slate-400" />
                  </div>
                  <div className="mt-5 space-y-4 text-slate-600">
                    {supportingInsights.length > 0 ? (
                      <ul className="space-y-3">
                        {supportingInsights.map((point, index) => (
                          <li key={point} className="flex gap-3 text-sm sm:text-base">
                            <span className="relative mt-1 h-2 w-2 flex-shrink-0 rounded-full bg-emerald-500" aria-hidden />
                            <span className="leading-relaxed">{point}.</span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm leading-relaxed sm:text-base">
                        {primaryInsight}
                      </p>
                    )}
                  </div>
                </div>

                <ROIPlanner />
              </div>

              <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-lg/20 shadow-slate-500/10 sm:p-8">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500">Experience Radar</p>
                    <h3 className="mt-1 text-lg font-semibold text-slate-900">How your funnel scores across trust, value, and flow</h3>
                  </div>
                  <p className="text-xs text-slate-500">Benchmark versus your previous run (when available)</p>
                </div>
                <div className="mt-6">
                  <ScoreComparisonChart currentScores={analysis.scores} previousScores={null} />
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
                <ScoreCard label="Clarity" score={analysis.scores.clarity} />
                <ScoreCard label="Value" score={analysis.scores.value} />
                <ScoreCard label="Proof" score={analysis.scores.proof} />
                <ScoreCard label="Design" score={analysis.scores.design} />
                <ScoreCard label="Flow" score={analysis.scores.flow} />
              </div>
            </section>

            {/* Journey Diagnostics */}
            <section id="journey" className="scroll-mt-32 space-y-6">
              <div className="flex flex-col gap-3">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500">Journey Diagnostics</p>
                    <h2 className="mt-2 text-2xl font-bold text-slate-900">Page-by-page narrative</h2>
                    <p className="mt-2 max-w-3xl text-sm text-slate-600">
                      Each page was scored against clarity, proof, and flow to surface experience gaps. Use these cards as a storyboard for how prospects move through your funnel.
                    </p>
                  </div>
                </div>
              </div>

              <CollapsibleSection
                id="page-breakdown"
                title="Detailed page analysis"
                icon={FiList}
                badge={`${analysis.pages.length} ${analysis.pages.length === 1 ? 'Page' : 'Pages'}`}
                defaultOpen
              >
                <div className="mt-6 space-y-6">
                  {analysis.pages.map((page, index) => (
                    <PageAnalysisCard key={index} page={page} index={index} />
                  ))}
                </div>
              </CollapsibleSection>
            </section>

            {/* Action Plan */}
            <section id="actions" className="scroll-mt-32 space-y-6">
              <div className="flex flex-col gap-3">
                <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500">Action Plan</p>
                <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
                  <h2 className="text-2xl font-bold text-slate-900">Prioritized roadmap to capture the lift</h2>
                  <button
                    onClick={() => scrollToSection('journey')}
                    className="inline-flex items-center gap-2 self-start rounded-full border border-slate-300 bg-white px-4 py-2 text-xs font-semibold uppercase tracking-wide text-slate-600 transition hover:border-slate-400 hover:text-slate-900"
                  >
                    Review diagnostics again
                  </button>
                </div>
              </div>

              <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-lg/20 shadow-slate-500/10 sm:p-8">
                <ActionableRecommendations analysis={analysis} />
              </div>

              <RerunCTA lastRunDate={analysis.created_at} urls={analysis.urls || []} position="bottom" />
            </section>

            {/* Momentum */}
            <section id="history" className="scroll-mt-32 space-y-6">
              <div className="flex flex-col gap-3">
                <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500">Momentum</p>
                <h2 className="text-2xl font-bold text-slate-900">Stay in rhythm with regular runs</h2>
                <p className="max-w-3xl text-sm text-slate-600">
                  Keep tracking improvements over time by re-running this analysis after meaningful updates. Historical trends will unlock once we have at least three completed reports on record.
                </p>
              </div>

              <div className="rounded-3xl border border-dashed border-slate-300 bg-slate-50 p-6 text-center text-slate-500 sm:p-10">
                <p className="text-sm font-medium">Report history timeline will appear here after your next run.</p>
                <p className="mt-1 text-xs text-slate-400">Re-run the analysis to begin charting progress.</p>
              </div>
            </section>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
