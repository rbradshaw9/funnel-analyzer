"use client"

import { useState } from 'react'
import { requestMagicLink, adminLogin } from '@/lib/api'

interface LoginButtonProps {
  className?: string
}

type LoginMode = 'magic' | 'admin'

export function LoginButton({ className }: LoginButtonProps) {
  const [open, setOpen] = useState(false)
  const [mode, setMode] = useState<LoginMode>('magic')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [statusMessage, setStatusMessage] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const resetState = () => {
    setMode('magic')
    setEmail('')
    setPassword('')
    setStatusMessage(null)
    setErrorMessage(null)
    setSubmitting(false)
  }

  const closeModal = () => {
    setOpen(false)
    resetState()
  }

  const handleMagicSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSubmitting(true)
    setStatusMessage(null)
    setErrorMessage(null)

    try {
      const response = await requestMagicLink(email)
      setStatusMessage(response.message ?? 'Check your inbox for your login link.')
    } catch (error: any) {
      setErrorMessage(error?.message || 'Unable to send magic link.')
    } finally {
      setSubmitting(false)
    }
  }

  const handleAdminSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSubmitting(true)
    setStatusMessage(null)
    setErrorMessage(null)

    try {
      const response = await adminLogin(email, password)
      const token = response.access_token
      if (token) {
        // Redirect so downstream auth flow can validate the token automatically.
        window.location.href = `/dashboard?token=${encodeURIComponent(token)}`
        return
      }
      setStatusMessage('Login successful. Redirecting to dashboard…')
    } catch (error: any) {
      setErrorMessage(error?.message || 'Invalid credentials.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className={[
          'text-sm font-semibold text-primary-600 hover:text-primary-700 transition-colors',
          className ?? '',
        ].filter(Boolean).join(' ')}
      >
        Log in
      </button>

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 px-4" role="dialog" aria-modal="true">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl" onClick={(event) => event.stopPropagation()}>
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-900">
                {mode === 'magic' ? 'Access your dashboard' : 'Admin login'}
              </h2>
              <button
                type="button"
                onClick={closeModal}
                className="text-slate-400 hover:text-slate-600"
                aria-label="Close login dialog"
              >
                ×
              </button>
            </div>

            <div className="mt-4 flex items-center gap-2 text-xs font-medium text-slate-500">
              <button
                type="button"
                onClick={() => { setMode('magic'); setStatusMessage(null); setErrorMessage(null); setSubmitting(false) }}
                className={`rounded-full px-3 py-1 transition-colors ${mode === 'magic' ? 'bg-primary-100 text-primary-700' : 'hover:bg-slate-100'}`}
              >
                Magic link
              </button>
              <button
                type="button"
                onClick={() => { setMode('admin'); setStatusMessage(null); setErrorMessage(null); setSubmitting(false) }}
                className={`rounded-full px-3 py-1 transition-colors ${mode === 'admin' ? 'bg-accent-100 text-accent-700' : 'hover:bg-slate-100'}`}
              >
                Admin
              </button>
            </div>

            {mode === 'magic' ? (
              <form className="mt-4 space-y-4" onSubmit={handleMagicSubmit}>
                <div>
                  <label htmlFor="login-email" className="block text-sm font-semibold text-slate-700">
                    Email address
                  </label>
                  <input
                    id="login-email"
                    type="email"
                    required
                    autoFocus
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-100"
                    placeholder="you@example.com"
                  />
                </div>

                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full rounded-xl bg-gradient-to-r from-primary-600 to-accent-500 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:from-primary-700 hover:to-accent-600 disabled:opacity-60"
                >
                  {submitting ? 'Sending magic link…' : 'Email me a login link'}
                </button>
              </form>
            ) : (
              <form className="mt-4 space-y-4" onSubmit={handleAdminSubmit}>
                <div>
                  <label htmlFor="admin-email" className="block text-sm font-semibold text-slate-700">
                    Admin email
                  </label>
                  <input
                    id="admin-email"
                    type="email"
                    required
                    autoFocus
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-100"
                    placeholder="admin@example.com"
                  />
                </div>
                <div>
                  <label htmlFor="admin-password" className="block text-sm font-semibold text-slate-700">
                    Password
                  </label>
                  <input
                    id="admin-password"
                    type="password"
                    required
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-100"
                    placeholder="••••••••"
                  />
                </div>

                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800 disabled:opacity-60"
                >
                  {submitting ? 'Signing in…' : 'Log in as admin'}
                </button>
              </form>
            )}

            {statusMessage && (
              <p className="mt-4 rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
                {statusMessage}
              </p>
            )}

            {errorMessage && (
              <p className="mt-4 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">
                {errorMessage}
              </p>
            )}
          </div>
        </div>
      )}
    </>
  )
}
