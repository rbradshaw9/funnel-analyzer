'use client'

import Link from 'next/link'
import type { ReactNode } from 'react'

interface TopNavProps {
  rightSlot?: ReactNode
  translucent?: boolean
  sticky?: boolean
  className?: string
}

export function TopNav({ rightSlot, translucent = true, sticky = true, className }: TopNavProps) {
  const headerClasses = [
    'border-b border-slate-200',
    translucent ? 'bg-white/85 backdrop-blur-md' : 'bg-white',
    sticky ? 'sticky top-0 z-40' : '',
    className ?? '',
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <header className={headerClasses}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <Link href="/" className="group flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600 text-white font-semibold flex items-center justify-center transition-transform group-hover:scale-105">
              FA
            </div>
            <span className="text-xl font-semibold text-slate-900 group-hover:text-indigo-700 transition-colors">
              Funnel Analyzer Pro
            </span>
          </Link>
          <div className="flex items-center gap-4">{rightSlot}</div>
        </div>
      </div>
    </header>
  )
}
