'use client'

import type { AuthMode } from './AuthModal'

interface AuthPromptCardProps {
  onSelectMode: (mode: AuthMode) => void
  statusMessage?: string | null
  errorMessage?: string | null
  disabled?: boolean
  showSignOut?: boolean
  onSignOut?: () => void
}

export function AuthPromptCard({
  onSelectMode,
  statusMessage,
  errorMessage,
  disabled = false,
  showSignOut = false,
  onSignOut,
}: AuthPromptCardProps) {
  return (
    <div className="w-full max-w-sm rounded-2xl border border-primary-100 bg-white/95 p-6 shadow-[0_28px_60px_-35px_rgba(79,70,229,0.65)] backdrop-blur">
      <h3 className="text-lg font-semibold text-gray-900">Unlock the full report</h3>
      <p className="mt-2 text-sm text-gray-600">
        Create your free account to view unblurred insights, save your analyses, and get upgrade-only conversion playbooks.
      </p>

      <ul className="mt-4 space-y-2 text-sm text-gray-600">
        <li className="flex items-start gap-2">
          <span className="mt-1 text-accent-500">•</span>
          <span>Store every analysis in your dashboard</span>
        </li>
        <li className="flex items-start gap-2">
          <span className="mt-1 text-accent-500">•</span>
          <span>Instant AI rewrite playbooks</span>
        </li>
        <li className="flex items-start gap-2">
          <span className="mt-1 text-accent-500">•</span>
          <span>Shareable exports for teams & clients</span>
        </li>
      </ul>

      {statusMessage && (
        <p className="mt-4 rounded-lg bg-indigo-50 px-3 py-2 text-sm text-indigo-700">{statusMessage}</p>
      )}

      {errorMessage && (
        <p className="mt-4 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{errorMessage}</p>
      )}

      <div className="mt-5 flex flex-col gap-3">
        <button
          type="button"
          onClick={() => onSelectMode('signup')}
          disabled={disabled}
          className="w-full rounded-xl bg-gradient-to-r from-primary-600 to-accent-500 px-4 py-3 text-sm font-semibold text-white shadow-lg transition-all hover:from-primary-700 hover:to-accent-600 disabled:cursor-not-allowed disabled:opacity-60"
        >
          Create free account
        </button>
        <button
          type="button"
          onClick={() => onSelectMode('login')}
          disabled={disabled}
          className="w-full rounded-xl border-2 border-primary-100 px-4 py-3 text-sm font-semibold text-primary-600 transition-all hover:border-primary-200 hover:text-primary-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          I already have an account
        </button>
        {showSignOut && (
          <button
            type="button"
            onClick={onSignOut}
            className="w-full rounded-xl border border-gray-200 px-4 py-2 text-xs font-semibold text-gray-500 transition hover:border-gray-300 hover:text-gray-700"
          >
            Sign out
          </button>
        )}
      </div>

      <p className="mt-4 text-center text-xs text-gray-400">
        No spam—just your reports and conversion insights.
      </p>
    </div>
  )
}
