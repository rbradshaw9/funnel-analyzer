'use client'

import Image from 'next/image'
import { motion } from 'framer-motion'
import { FiMaximize2 } from 'react-icons/fi'
import { ScreenshotHotspot, ScreenshotHotspotPosition, ScreenshotHotspotTheme } from '@/types'

interface ScreenshotCalloutProps {
  imageUrl: string
  alt: string
  caption?: string
  hotspot?: ScreenshotHotspot | null
  onOpenFull?: () => void
}

const themeMap: Record<ScreenshotHotspotTheme, { base: string; text: string; accent: string }> = {
  emerald: {
    base: 'bg-emerald-500/90',
    text: 'text-white',
    accent: 'from-emerald-400/40 via-transparent to-transparent',
  },
  sky: {
    base: 'bg-sky-500/90',
    text: 'text-white',
    accent: 'from-sky-400/40 via-transparent to-transparent',
  },
  violet: {
    base: 'bg-violet-500/90',
    text: 'text-white',
    accent: 'from-violet-400/40 via-transparent to-transparent',
  },
  amber: {
    base: 'bg-amber-500/90',
    text: 'text-slate-900',
    accent: 'from-amber-300/40 via-transparent to-transparent',
  },
  rose: {
    base: 'bg-rose-500/90',
    text: 'text-white',
    accent: 'from-rose-400/40 via-transparent to-transparent',
  },
}

const positionMap: Record<ScreenshotHotspotPosition, string> = {
  center: 'top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2',
  top: 'top-6 left-1/2 -translate-x-1/2',
  bottom: 'bottom-6 left-1/2 -translate-x-1/2',
  left: 'left-6 top-1/2 -translate-y-1/2',
  right: 'right-6 top-1/2 -translate-y-1/2',
  'top-left': 'top-6 left-6',
  'top-right': 'top-6 right-6',
  'bottom-left': 'bottom-6 left-6',
  'bottom-right': 'bottom-6 right-6',
}

function getPositionClasses(position?: ScreenshotHotspotPosition) {
  if (!position) return positionMap.center
  return positionMap[position] ?? positionMap.center
}

function getTheme(theme?: ScreenshotHotspotTheme) {
  if (!theme) return themeMap.emerald
  return themeMap[theme] ?? themeMap.emerald
}

export default function ScreenshotCallout({ imageUrl, alt, caption, hotspot, onOpenFull }: ScreenshotCalloutProps) {
  const theme = getTheme(hotspot?.theme)
  const positionClasses = getPositionClasses(hotspot?.position)
  const isInteractive = Boolean(onOpenFull)

  const handleOpen = () => {
    if (onOpenFull) {
      onOpenFull()
    }
  }

  return (
    <div className="relative overflow-hidden rounded-2xl border border-slate-200 shadow-sm">
      <div
        className={`relative h-52 w-full overflow-hidden bg-slate-100 ${isInteractive ? 'cursor-zoom-in outline-none focus-visible:ring-2 focus-visible:ring-primary-500' : ''}`}
        role={isInteractive ? 'button' : undefined}
        tabIndex={isInteractive ? 0 : undefined}
        onClick={handleOpen}
        onKeyDown={(event) => {
          if (!isInteractive) return
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault()
            handleOpen()
          }
        }}
      >
        <Image
          src={imageUrl}
          alt={alt}
          fill
          className="object-cover object-top"
          sizes="(min-width: 1024px) 320px, 100vw"
        />

        {hotspot && (
          <>
            <div className="absolute inset-0 bg-gradient-to-b from-slate-900/0 via-slate-900/0 to-slate-900/10 pointer-events-none" />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 12 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              transition={{ duration: 0.25, ease: 'easeOut' }}
              className={`absolute z-10 max-w-[80%] rounded-xl px-4 py-3 shadow-lg backdrop-blur ${theme.base} ${theme.text} ${positionClasses}`}
            >
              <p className="text-xs font-semibold tracking-wide uppercase opacity-80">Focus</p>
              <p className="text-sm font-semibold leading-snug">{hotspot.label}</p>
              {hotspot.description && <p className="mt-1 text-xs opacity-80 leading-snug">{hotspot.description}</p>}
            </motion.div>
            <div className={`pointer-events-none absolute inset-0 bg-gradient-to-br ${theme.accent}`} />
          </>
        )}

        {onOpenFull && (
          <button
            onClick={(event) => {
              event.stopPropagation()
              handleOpen()
            }}
            className="absolute bottom-3 right-3 inline-flex items-center gap-1 rounded-full border border-white/70 bg-white/80 px-3 py-1.5 text-xs font-semibold text-slate-700 shadow-sm backdrop-blur transition hover:bg-white"
            type="button"
          >
            <FiMaximize2 className="h-3.5 w-3.5" />
            Expand
          </button>
        )}
      </div>

      {caption && (
        <div className="border-t border-slate-200 bg-white px-4 py-3 text-xs text-slate-600">
          {caption}
        </div>
      )}
    </div>
  )
}
