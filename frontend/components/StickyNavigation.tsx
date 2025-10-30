'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FiFileText, FiList, FiCheckSquare, FiClock, FiChevronRight } from 'react-icons/fi'

interface Section {
  id: string
  label: string
  icon: React.ElementType
  completionBadge?: number
}

interface StickyNavigationProps {
  sections: Section[]
  completionPercentage: number
  variant?: 'floating' | 'sidebar'
}

export default function StickyNavigation({ sections, completionPercentage, variant = 'floating' }: StickyNavigationProps) {
  const [activeSection, setActiveSection] = useState('')
  const [isVisible, setIsVisible] = useState(variant === 'sidebar')

  useEffect(() => {
    const handleScroll = () => {
      if (variant === 'floating') {
        // Show nav after scrolling 200px
        setIsVisible(window.scrollY > 200)
      }

      // Find active section
      for (const section of sections) {
        const element = document.getElementById(section.id)
        if (element) {
          const rect = element.getBoundingClientRect()
          if (rect.top <= 150 && rect.bottom >= 150) {
            setActiveSection(section.id)
            break
          }
        }
      }
    }

    window.addEventListener('scroll', handleScroll)
    handleScroll()
    return () => window.removeEventListener('scroll', handleScroll)
  }, [sections, variant])

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id)
    if (element) {
      const top = element.offsetTop - 120
      window.scrollTo({ top, behavior: 'smooth' })
    }
  }

  if (variant === 'sidebar') {
    return (
      <div className="sticky top-28">
        <div className="bg-white rounded-3xl shadow-xl border border-slate-200 p-5">
          <div className="mb-5 pb-4 border-b border-slate-200">
            <div className="flex items-center justify-between mb-3">
              <div>
                <p className="text-xs font-semibold tracking-wide text-slate-500 uppercase">Report Progress</p>
                <h3 className="text-lg font-bold text-slate-900">Navigation</h3>
              </div>
              <div className="text-xs font-semibold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full">
                {completionPercentage}%
              </div>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-1.5">
              <div
                className="bg-gradient-to-r from-emerald-500 via-teal-500 to-sky-500 h-1.5 rounded-full transition-all duration-500"
                style={{ width: `${completionPercentage}%` }}
              />
            </div>
          </div>

          <nav className="space-y-1.5">
            {sections.map((section) => {
              const Icon = section.icon
              const isActive = activeSection === section.id

              return (
                <button
                  key={section.id}
                  onClick={() => scrollToSection(section.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all text-left ${
                    isActive
                      ? 'bg-slate-900 text-white shadow-lg'
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                  }`}
                >
                  <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                  <div className="flex-1">
                    <p className={`text-sm font-semibold ${isActive ? 'text-white' : 'text-slate-800'}`}>
                      {section.label}
                    </p>
                    <p className="text-xs text-slate-500">
                      Scroll to section
                    </p>
                  </div>
                  {section.completionBadge !== undefined && (
                    <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                      isActive 
                        ? 'bg-white/20 text-white' 
                        : 'bg-slate-100 text-slate-600'
                    }`}>
                      {section.completionBadge}
                    </span>
                  )}
                  {isActive && <FiChevronRight className="w-4 h-4" />}
                </button>
              )
            })}
          </nav>
        </div>
      </div>
    )
  }

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 20, scale: 0.95 }}
          className="fixed bottom-6 right-4 sm:right-6 lg:right-10 lg:bottom-10 z-50"
        >
          <div className="bg-white rounded-2xl shadow-xl border border-slate-200 p-4 w-64">
            {/* Header */}
            <div className="mb-4 pb-4 border-b border-slate-200">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-bold text-slate-900">Quick Navigation</h3>
                <div className="text-xs font-semibold text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full">
                  {completionPercentage}%
                </div>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-1.5">
                <div 
                  className="bg-gradient-to-r from-emerald-500 to-teal-500 h-1.5 rounded-full transition-all duration-500"
                  style={{ width: `${completionPercentage}%` }}
                />
              </div>
            </div>

            {/* Navigation Links */}
            <nav className="space-y-1">
              {sections.map((section) => {
                const Icon = section.icon
                const isActive = activeSection === section.id

                return (
                  <button
                    key={section.id}
                    onClick={() => scrollToSection(section.id)}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                      isActive
                        ? 'bg-emerald-50 text-emerald-700'
                        : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                    }`}
                  >
                    <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? 'text-emerald-600' : ''}`} />
                    <span className={`flex-1 text-left text-sm ${isActive ? 'font-semibold' : 'font-medium'}`}>
                      {section.label}
                    </span>
                    {section.completionBadge !== undefined && (
                      <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                        isActive 
                          ? 'bg-emerald-100 text-emerald-700' 
                          : 'bg-slate-100 text-slate-600'
                      }`}>
                        {section.completionBadge}
                      </span>
                    )}
                    {isActive && <FiChevronRight className="w-4 h-4 text-emerald-600" />}
                  </button>
                )
              })}
            </nav>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
