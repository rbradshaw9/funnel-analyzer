'use client'

import Link from 'next/link'

interface LogoProps {
  showWordmark?: boolean
  href?: string
  className?: string
}

export function Logo({ showWordmark = true, href = '/', className = '' }: LogoProps) {
  const wordmark = showWordmark ? (
    <span className="flex flex-col leading-tight">
      <span className="text-[0.85rem] font-semibold uppercase tracking-[0.32em] text-slate-400">
        Funnel
      </span>
      <span className="text-xl font-semibold text-slate-900">
        Analyzer <span className="text-primary-600">Pro</span>
      </span>
    </span>
  ) : null

  return (
    <Link href={href} className={`group flex items-center gap-3 ${className}`}>
      <span className="relative grid h-11 w-11 place-items-center rounded-2xl bg-slate-950 text-white shadow-[0_12px_30px_-12px_rgba(37,99,235,0.6)] transition-transform group-hover:scale-[1.04]">
        <span className="absolute inset-0 rounded-2xl bg-gradient-to-br from-primary-500 via-primary-600 to-accent-500 opacity-95" />
        <span className="absolute -bottom-1 inset-x-1 h-2 rounded-full bg-gradient-to-r from-accent-500/50 to-primary-500/60 blur-md" />
        <span className="relative flex items-center gap-1 text-sm font-bold tracking-tight">
          <span className="rounded-full bg-white/90 px-1.5 py-0.5 text-[0.65rem] font-semibold uppercase text-slate-900 shadow-sm">
            FA
          </span>
          <span className="text-[0.65rem] uppercase tracking-[0.18em] text-white/80">AI</span>
        </span>
      </span>
      {wordmark}
    </Link>
  )
}
