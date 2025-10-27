'use client'

import { useEffect, useState } from 'react'

import { requestMagicLink } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'

export type AuthMode = 'signup' | 'login'

interface AuthModalProps {
  open: boolean
  onClose: () => void
  defaultMode?: AuthMode
}
const EMAIL_PLACEHOLDER = 'taylor@example.com'

export function AuthModal({ open, onClose, defaultMode = 'signup' }: AuthModalProps) {
  const [mode, setMode] = useState<AuthMode>(defaultMode)
  const [email, setEmail] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const setError = useAuthStore((state) => state.setError)

  useEffect(() => {
    if (!open) {
      return
    }
    setMode(defaultMode)
    setSuccessMessage(null)
    setErrorMessage(null)
  }, [defaultMode, open])

  if (!open) {
    return null
  }

  const resetForm = () => {
    setEmail('')
    setSuccessMessage(null)
    setErrorMessage(null)
    setSubmitting(false)
    setError(null)
  }

  const handleClose = () => {
    resetForm()
    onClose()
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (submitting || successMessage) {
      return
    }

    setSubmitting(true)
    setErrorMessage(null)
    setSuccessMessage(null)

    const normalizedEmail = email.trim().toLowerCase()
    if (!normalizedEmail) {
      setErrorMessage('Please enter a valid email address to continue.')
      setSubmitting(false)
      return
    }
    try {
      const response = await requestMagicLink(normalizedEmail)

      const message =
        response.message ??
        (mode === 'signup'
          ? 'Check your email for a secure link to confirm your account.'
          : 'Check your email for a secure login link.')

      setSuccessMessage(message)
      setError(null)
    } catch (error: any) {
      const message = error?.message || 'We could not process your request. Please try again.'
      setErrorMessage(message)
      setError(message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 px-4"
      role="dialog"
      aria-modal="true"
      onClick={handleClose}
    >
      <div
        className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">
            {mode === 'signup' ? 'Create your Funnel Analyzer account' : 'Log in to Funnel Analyzer'}
          </h2>
          <button
            type="button"
            onClick={handleClose}
            className="text-2xl leading-none text-slate-400 transition hover:text-slate-600"
            aria-label="Close authentication dialog"
          >
            ×
          </button>
        </div>

        <div className="mt-4 flex items-center gap-2 text-xs font-medium text-slate-500">
          <button
            type="button"
            onClick={() => {
              setMode('signup')
              setSuccessMessage(null)
              setErrorMessage(null)
            }}
            className={`rounded-full px-3 py-1 transition-colors ${mode === 'signup' ? 'bg-primary-100 text-primary-700' : 'hover:bg-slate-100'}`}
          >
            Create account
          </button>
          <button
            type="button"
            onClick={() => {
              setMode('login')
              setSuccessMessage(null)
              setErrorMessage(null)
            }}
            className={`rounded-full px-3 py-1 transition-colors ${mode === 'login' ? 'bg-accent-100 text-accent-700' : 'hover:bg-slate-100'}`}
          >
            Log in
          </button>
        </div>

        <form className="mt-4 space-y-4" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="auth-email" className="block text-sm font-semibold text-slate-700">
              Email address
            </label>
            <input
              id="auth-email"
              type="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder={EMAIL_PLACEHOLDER}
              className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-100"
              autoComplete="email"
            />
            <p className="mt-1 text-xs text-slate-500">
              {mode === 'signup'
                ? 'We will email you a secure link to confirm your account and unlock your report.'
                : 'We will email you a secure login link. Open it on this device to unlock your report.'}
            </p>
          </div>

          <button
            type="submit"
            className="w-full rounded-xl bg-gradient-to-r from-primary-600 to-accent-500 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:from-primary-700 hover:to-accent-600 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={submitting || Boolean(successMessage)}
          >
            {submitting
              ? 'Sending magic link…'
              : mode === 'signup'
                ? 'Email me an unlock link'
                : 'Email me a login link'}
          </button>
        </form>

        {successMessage && (
          <p className="mt-4 rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-700">{successMessage}</p>
        )}

        {errorMessage && (
          <p className="mt-4 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{errorMessage}</p>
        )}

        <p className="mt-4 text-center text-xs text-slate-400">
          By continuing, you agree to our terms of service and privacy policy.
        </p>
      </div>
    </div>
  )
}
