'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center">
                <span className="text-white text-xl font-bold">FA</span>
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                Funnel Analyzer Pro
              </h1>
            </div>
            <div className="flex items-center gap-4">
              <Link href="/free-analysis" className="text-gray-600 hover:text-gray-900 font-medium">
                Free Analysis
              </Link>
              <a
                href="https://smarttoolclub.com"
                className="px-6 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all shadow-md"
              >
                Join Club
              </a>
            </div>
          </div>
        </div>
      </header>

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
            <div className="bg-white rounded-2xl shadow-2xl p-8 border border-gray-200">
              <div className="text-center mb-6">
                <div className="text-6xl font-extrabold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent mb-2">
                  87
                </div>
                <div className="text-sm text-gray-500 font-medium">Overall Score</div>
              </div>
              
              <div className="space-y-3">
                {[
                  { label: 'Clarity', score: 92, color: 'bg-blue-500' },
                  { label: 'Value', score: 85, color: 'bg-purple-500' },
                  { label: 'Proof', score: 78, color: 'bg-yellow-500' },
                  { label: 'Design', score: 90, color: 'bg-pink-500' },
                  { label: 'Flow', score: 88, color: 'bg-green-500' },
                ].map((metric) => (
                  <div key={metric.label}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-700 font-medium">{metric.label}</span>
                      <span className="text-gray-900 font-bold">{metric.score}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`${metric.color} h-2 rounded-full transition-all duration-500`}
                        style={{ width: `${metric.score}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Floating badge */}
            <div className="absolute -top-4 -right-4 bg-gradient-to-r from-orange-500 to-pink-500 text-white px-6 py-3 rounded-full shadow-xl font-bold text-sm">
              ⚡ Instant Results
            </div>
          </motion.div>
        </div>
      </section>

      {/* Social Proof */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-200">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-indigo-600 mb-2">2,500+</div>
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
            <a href="https://smarttoolclub.com/join" className="text-indigo-600 hover:text-indigo-700 font-semibold">
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
                <li><a href="https://smarttoolclub.com" className="hover:text-white">Smart Tool Club</a></li>
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
