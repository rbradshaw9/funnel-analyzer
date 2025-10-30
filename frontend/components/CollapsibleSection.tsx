'use client'

import { useState, useEffect, ReactNode } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FiChevronDown, FiChevronUp } from 'react-icons/fi'

interface CollapsibleSectionProps {
  id: string
  title: string
  defaultOpen?: boolean
  children: ReactNode
  badge?: string | number
  icon?: React.ElementType
}

export default function CollapsibleSection({ 
  id, 
  title, 
  defaultOpen = true, 
  children, 
  badge,
  icon: Icon 
}: CollapsibleSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen)
  const storageKey = `section-${id}-open`

  // Load saved state from localStorage
  useEffect(() => {
    const saved = localStorage.getItem(storageKey)
    if (saved !== null) {
      setIsOpen(saved === 'true')
    }
  }, [storageKey])

  // Save state to localStorage
  const handleToggle = () => {
    const newState = !isOpen
    setIsOpen(newState)
    localStorage.setItem(storageKey, String(newState))
  }

  return (
    <div id={id} className="scroll-mt-24">
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {/* Header */}
        <button
          onClick={handleToggle}
          className="w-full flex items-center justify-between p-6 hover:bg-slate-50 transition-colors"
        >
          <div className="flex items-center gap-4">
            {Icon && (
              <div className="p-2 bg-emerald-100 rounded-lg">
                <Icon className="w-5 h-5 text-emerald-600" />
              </div>
            )}
            <div className="text-left">
              <h2 className="text-2xl font-bold text-slate-900">{title}</h2>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {badge && (
              <span className="px-3 py-1 bg-emerald-100 text-emerald-700 rounded-full text-sm font-semibold">
                {badge}
              </span>
            )}
            <div className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
              {isOpen ? (
                <FiChevronUp className="w-5 h-5 text-slate-600" />
              ) : (
                <FiChevronDown className="w-5 h-5 text-slate-600" />
              )}
            </div>
          </div>
        </button>

        {/* Content */}
        <AnimatePresence initial={false}>
          {isOpen && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3, ease: 'easeInOut' }}
            >
              <div className="px-6 pb-6 border-t border-slate-100">
                {children}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
