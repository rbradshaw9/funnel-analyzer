'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { FiBarChart2, FiZap, FiTrendingUp, FiCheckCircle } from 'react-icons/fi'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      {/* Navigation */}
      <nav className="border-b border-slate-200 bg-white/80 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <FiBarChart2 className="text-primary-600 text-2xl" />
              <span className="text-xl font-semibold text-slate-900">Funnel Analyzer Pro</span>
            </div>
            <Link 
              href="/dashboard"
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center"
        >
          <h1 className="text-5xl md:text-6xl font-bold text-slate-900 mb-6">
            AI-Powered Funnel Analysis
          </h1>
          <p className="text-xl text-slate-600 mb-8 max-w-2xl mx-auto">
            Get instant, actionable insights on your marketing funnels. 
            Analyze clarity, value, design, and flow with GPT-4o intelligence.
          </p>
          <Link
            href="/dashboard"
            className="inline-block px-8 py-4 bg-primary-600 text-white text-lg rounded-lg hover:bg-primary-700 transition-colors shadow-soft-lg"
          >
            Start Analyzing Now
          </Link>
        </motion.div>

        {/* Features Grid */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="grid md:grid-cols-3 gap-8 mt-24"
        >
          <FeatureCard
            icon={<FiZap className="text-3xl" />}
            title="Lightning Fast"
            description="Get comprehensive funnel analysis in seconds, not hours"
          />
          <FeatureCard
            icon={<FiTrendingUp className="text-3xl" />}
            title="AI-Powered Insights"
            description="GPT-4o analyzes your funnel like a conversion expert"
          />
          <FeatureCard
            icon={<FiCheckCircle className="text-3xl" />}
            title="Actionable Reports"
            description="Clear scores and specific recommendations to improve conversions"
          />
        </motion.div>

        {/* How It Works */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-24"
        >
          <h2 className="text-3xl font-bold text-center text-slate-900 mb-12">
            How It Works
          </h2>
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
        </motion.div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 mt-32 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-slate-600">
          <p>&copy; 2025 Funnel Analyzer Pro. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="p-6 bg-white rounded-xl shadow-soft hover:shadow-soft-lg transition-shadow">
      <div className="text-primary-600 mb-4">{icon}</div>
      <h3 className="text-xl font-semibold text-slate-900 mb-2">{title}</h3>
      <p className="text-slate-600">{description}</p>
    </div>
  )
}

function StepCard({ number, title, description }: { number: string; title: string; description: string }) {
  return (
    <div className="text-center">
      <div className="w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
        {number}
      </div>
      <h3 className="text-xl font-semibold text-slate-900 mb-2">{title}</h3>
      <p className="text-slate-600">{description}</p>
    </div>
  )
}
