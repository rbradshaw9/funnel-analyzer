'use client';

import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { TopNav } from '@/components/TopNav';
import { SMART_TOOL_CLUB_JOIN_URL } from '@/lib/externalLinks';
import { getPublicStats } from '@/lib/api';

export default function Home() {
  const metrics = [
    {
      label: 'Clarity',
      score: 92,
      gradient: 'from-sky-400 to-sky-500',
      description: 'Examines how quickly the page communicates the offer, measures headline strength, message consistency, and whether visitors instantly know what to do next.',
    },
    {
      label: 'Value',
      score: 85,
      gradient: 'from-violet-500 to-fuchsia-500',
      description: 'Evaluates how compelling the value proposition is, checking benefit framing, differentiation, objection handling, and perceived ROI for the visitor.',
    },
    {
      label: 'Proof',
      score: 78,
      gradient: 'from-amber-400 to-orange-500',
      description: 'Scores the depth of social proof, credibility assets, data points, and trust signals that reassure buyers they are making the right decision.',
    },
    {
      label: 'Design',
      score: 90,
      gradient: 'from-rose-400 to-pink-500',
      description: 'Reviews visual hierarchy, readability, accessibility, and responsiveness to ensure the layout guides attention and feels premium on every device.',
    },
    {
      label: 'Flow',
      score: 88,
      gradient: 'from-emerald-400 to-teal-500',
      description: 'Checks the conversion journey for friction—CTA placement, step sequencing, load speed cues, and how smoothly visitors progress to the next action.',
    },
  ] as const

  type Metric = (typeof metrics)[number]

  const [activeMetric, setActiveMetric] = useState<Metric | null>(null)
  const [pagesAnalyzedTarget, setPagesAnalyzedTarget] = useState<number | null>(null)
  const [displayedPagesAnalyzed, setDisplayedPagesAnalyzed] = useState(0)
  const animationFrameRef = useRef<number | null>(null)
  const animationStartRef = useRef<number | null>(null)
  const displayedPagesRef = useRef(0)

  const overallScore = Math.round(metrics.reduce((acc, metric) => acc + metric.score, 0) / metrics.length)
  const overallScoreDeg = overallScore * 3.6

  useEffect(() => {
    displayedPagesRef.current = displayedPagesAnalyzed
  }, [displayedPagesAnalyzed])

  useEffect(() => {
    let isMounted = true

    const fetchStats = async () => {
      try {
        const stats = await getPublicStats()
        if (!isMounted) {
          return
        }
        setPagesAnalyzedTarget(Math.max(stats.pages_analyzed ?? 0, 0))
      } catch (error) {
        console.warn('Failed to load public stats', error)
      }
    }

    fetchStats()
    const intervalId = setInterval(fetchStats, 60_000)

    return () => {
      isMounted = false
      clearInterval(intervalId)
    }
  }, [])

  useEffect(() => {
    if (pagesAnalyzedTarget === null) {
      return
    }

    if (animationFrameRef.current !== null) {
      cancelAnimationFrame(animationFrameRef.current)
    }

    animationStartRef.current = null
    const startingValue = displayedPagesRef.current
    const targetValue = Math.max(pagesAnalyzedTarget, 0)

    if (startingValue === targetValue) {
      return
    }

    const duration = 1_500

    const step = (timestamp: number) => {
      if (animationStartRef.current === null) {
        animationStartRef.current = timestamp
      }

      const progress = Math.min((timestamp - animationStartRef.current) / duration, 1)
      const nextValue = Math.round(startingValue + (targetValue - startingValue) * progress)
      setDisplayedPagesAnalyzed(nextValue)

      if (progress < 1) {
        animationFrameRef.current = requestAnimationFrame(step)
      }
    }

    animationFrameRef.current = requestAnimationFrame(step)

    return () => {
      if (animationFrameRef.current !== null) {
        cancelAnimationFrame(animationFrameRef.current)
        animationFrameRef.current = null
      }
    }
  }, [pagesAnalyzedTarget])

  useEffect(() => {
    return () => {
      if (animationFrameRef.current !== null) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [])

  const pagesAnalyzedDisplay = pagesAnalyzedTarget === null
    ? '—'
    : `${Math.max(displayedPagesAnalyzed, 0).toLocaleString()}+`

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <TopNav
        rightSlot={
          <div className="flex items-center gap-4">
            <Link href="/free-analysis" className="text-sm font-medium text-slate-600 hover:text-slate-900">
              Free Analysis
            </Link>
            <a
              href={SMART_TOOL_CLUB_JOIN_URL}
              className="inline-flex items-center px-5 py-2 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-sm font-semibold shadow-md hover:from-indigo-700 hover:to-purple-700 transition-colors"
            >
              Join Club
            </a>
          </div>
        }
      />

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Column */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="inline-block px-4 py-2 bg-indigo-100 text-indigo-700 rounded-full text-sm font-semibold mb-6">
              ✨ Powered by GPT-4o AI
            </div>
            
            <h2 className="text-5xl lg:text-6xl font-extrabold text-gray-900 mb-6 leading-tight">
              Turn Your Marketing Pages Into
              <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                {' '}Conversion Machines
              </span>
            </h2>
            
            <p className="text-xl text-gray-600 mb-8 leading-relaxed">
              Get instant, AI-powered analysis of your sales pages, landing pages, and funnels. 
              Discover exactly what&apos;s working, what&apos;s not, and how to boost conversions.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 mb-8">
              <Link
                href="/free-analysis"
                className="px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl text-center"
              >
                Start Free Analysis →
              </Link>
              <a
                href="#how-it-works"
                className="px-8 py-4 bg-white text-gray-700 font-semibold rounded-xl hover:bg-gray-50 transition-all shadow-md border-2 border-gray-200 text-center"
              >
                See How It Works
              </a>
            </div>

            <div className="flex items-center gap-6 text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>No signup required</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Results in 60 seconds</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>100% free to try</span>
              </div>
            </div>
          </motion.div>

          {/* Right Column - Visual */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="relative"
          >
            <div className="absolute -top-5 -right-4 bg-gradient-to-r from-orange-500 to-pink-500 text-white px-6 py-3 rounded-full shadow-xl font-semibold text-sm">
              ⚡ 60s Funnel Insights
            </div>
            <div className="bg-white rounded-3xl shadow-2xl p-10 border border-slate-200">
              <div className="flex flex-col items-center mb-10">
                <div
                  className="relative flex items-center justify-center w-48 h-48 rounded-full shadow-[0_25px_60px_rgba(99,102,241,0.25)]"
                  style={{
                    background: `conic-gradient(#4f46e5 ${overallScoreDeg}deg, #e2e8f0 ${overallScoreDeg}deg)`
                  }}
                >
                  <div className="absolute inset-4 rounded-full bg-white flex flex-col items-center justify-center shadow-inner">
                    <span className="text-4xl font-extrabold text-slate-900">{overallScore}</span>
                    <span className="text-xs uppercase tracking-wider text-slate-500 mt-1">Overall score</span>
                  </div>
                </div>
                <p className="mt-6 text-center text-sm text-slate-500 max-w-xs">
                  Balanced average across clarity, value, proof, design, and flow—highlighting the biggest conversion wins.
                </p>
              </div>

              <div className="space-y-4">
                {metrics.map((metric) => (
                  <button
                    type="button"
                    key={metric.label}
                    onClick={() => setActiveMetric(metric)}
                    className="w-full rounded-2xl border border-slate-200 p-4 text-left shadow-sm transition hover:shadow-md bg-white/60"
                    aria-label={`Explain the ${metric.label} score`}
                  >
                    <div className="flex items-center justify-between text-sm mb-2">
                      <div>
                        <span className="font-semibold text-slate-900">{metric.label}</span>
                        <span className="ml-2 text-xs text-slate-400">Target ≥ 85</span>
                      </div>
                      <span className="text-base font-bold text-slate-900">{metric.score}</span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                      <div
                        className={`h-full bg-gradient-to-r ${metric.gradient}`}
                        style={{ width: `${metric.score}%` }}
                      />
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {activeMetric && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 px-4"
          onClick={() => setActiveMetric(null)}
        >
          <div
            className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <h3 className="text-lg font-semibold text-slate-900">
                  {activeMetric.label} score
                </h3>
                <p className="mt-1 text-sm text-slate-500">Target ≥ 85 · Current {activeMetric.score}</p>
              </div>
              <button
                type="button"
                onClick={() => setActiveMetric(null)}
                className="text-slate-400 hover:text-slate-600"
                aria-label="Close metric explanation"
              >
                ×
              </button>
            </div>
            <p className="mt-4 text-sm leading-relaxed text-slate-600">
              {activeMetric.description}
            </p>
            <button
              type="button"
              onClick={() => setActiveMetric(null)}
              className="mt-6 w-full rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800 transition"
            >
              Got it
            </button>
          </div>
        </div>
      )}

      {/* Social Proof */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-200">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-indigo-600 mb-2">{pagesAnalyzedDisplay}</div>
              <div className="text-sm text-gray-600">Pages Analyzed</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-indigo-600 mb-2">87%</div>
              <div className="text-sm text-gray-600">Avg. Score Improvement</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-indigo-600 mb-2">10s</div>
              <div className="text-sm text-gray-600">Average Analysis Time</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-indigo-600 mb-2">24/7</div>
              <div className="text-sm text-gray-600">Instant Availability</div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h3 className="text-4xl font-extrabold text-gray-900 mb-4">
            How It Works
          </h3>
          <p className="text-xl text-gray-600">
            Get professional-grade funnel analysis in three simple steps
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <StepCard
            number="1"
            title="Enter Your URLs"
            description="Add URLs for your sales page, checkout, upsells, and thank you page"
          />
          <StepCard
            number="2"
            title="AI Analysis"
            description="Our AI scrapes content and analyzes clarity, value, proof, design, and flow"
          />
          <StepCard
            number="3"
            title="Get Your Report"
            description="Receive detailed scores, insights, and actionable recommendations"
          />
        </div>
      </section>

      {/* Features */}
      <section className="bg-gradient-to-r from-indigo-600 to-purple-600 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h3 className="text-4xl font-extrabold text-white mb-4">
              Everything You Need to Optimize
            </h3>
            <p className="text-xl text-indigo-100">
              Comprehensive analysis powered by artificial intelligence
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { icon: '💬', title: 'Message Clarity', desc: 'Ensure visitors instantly understand your offer' },
              { icon: '💎', title: 'Value Proposition', desc: 'Strengthen your unique selling points' },
              { icon: '⭐', title: 'Social Proof', desc: 'Build trust with testimonials and credibility signals' },
              { icon: '🎨', title: 'Design Analysis', desc: 'Optimize visual hierarchy and mobile experience' },
              { icon: '🎯', title: 'Conversion Flow', desc: 'Remove friction from your customer journey' },
              { icon: '🧪', title: 'A/B Test Ideas', desc: 'Get specific split test recommendations' },
            ].map((feature, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.4, delay: idx * 0.05 }}
                viewport={{ once: true }}
                className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all"
              >
                <div className="text-4xl mb-3">{feature.icon}</div>
                <h4 className="text-xl font-bold text-white mb-2">{feature.title}</h4>
                <p className="text-indigo-100">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-3xl p-12 text-center border border-indigo-200">
          <h3 className="text-4xl font-extrabold text-gray-900 mb-4">
            Ready to Optimize Your Funnel?
          </h3>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Join thousands of marketers using AI to improve their conversion rates.
            Start with a free analysis - no credit card required.
          </p>
          
          <Link
            href="/free-analysis"
            className="inline-block px-10 py-5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold text-lg rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all shadow-xl hover:shadow-2xl hover:scale-105"
          >
            Analyze Your Page Free →
          </Link>

          <p className="text-sm text-gray-500 mt-6">
            Want full access to multi-page funnels and advanced features?{' '}
            <a href={SMART_TOOL_CLUB_JOIN_URL} className="text-indigo-600 hover:text-indigo-700 font-semibold">
              Join Smart Tool Club
            </a>
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <h4 className="text-white font-bold mb-4">Funnel Analyzer Pro</h4>
              <p className="text-sm">
                AI-powered funnel analysis to help you convert more visitors into customers.
              </p>
            </div>
            <div>
              <h4 className="text-white font-bold mb-4">Product</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="/free-analysis" className="hover:text-white">Free Analysis</Link></li>
                <li><a href={SMART_TOOL_CLUB_JOIN_URL} className="hover:text-white">Smart Tool Club</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-bold mb-4">Company</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="https://smarttoolclub.com/about" className="hover:text-white">About</a></li>
                <li><a href="https://smarttoolclub.com/contact" className="hover:text-white">Contact</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm">
            <p>&copy; 2025 Smart Tool Club. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

function StepCard({ number, title, description }: { number: string; title: string; description: string }) {
  return (
    <div className="text-center">
      <div className="w-12 h-12 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
        {number}
      </div>
      <h3 className="text-xl font-semibold text-slate-900 mb-2">{title}</h3>
      <p className="text-slate-600">{description}</p>
    </div>
  )
}
