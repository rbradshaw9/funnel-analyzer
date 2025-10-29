'use client'

import { useState } from 'react'
import { setUserPassword } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'

interface SetPasswordModalProps {
  open: boolean
  onClose: () => void
  onPasswordSet?: () => void
}

export function SetPasswordModal({ open, onClose, onPasswordSet }: SetPasswordModalProps) {
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const token = useAuthStore((state) => state.token)

  if (!open) {
    return null
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMessage(null)

    if (password.length < 8) {
      setErrorMessage('Password must be at least 8 characters long')
      return
    }

    if (password !== confirmPassword) {
      setErrorMessage('Passwords do not match')
      return
    }

    if (!token) {
      setErrorMessage('Not authenticated. Please log in again.')
      return
    }

    setSubmitting(true)

    try {
      await setUserPassword(token, password)
      setPassword('')
      setConfirmPassword('')
      onPasswordSet?.()
      onClose()
    } catch (error: any) {
      setErrorMessage(error.message || 'Failed to set password')
    } finally {
      setSubmitting(false)
    }
  }

  const handleSkip = () => {
    setPassword('')
    setConfirmPassword('')
    setErrorMessage(null)
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
      <div className="relative w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
        <button
          type="button"
          onClick={handleSkip}
          className="absolute right-4 top-4 rounded-lg p-1 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600"
          aria-label="Skip"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <div className="mb-6">
          <h2 className="text-2xl font-bold text-slate-900">Set up a password</h2>
          <p className="mt-2 text-sm text-slate-600">
            Add a password to your account for faster login next time. You can skip this step and set it up later.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-slate-700">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-100"
              autoComplete="new-password"
              minLength={8}
              disabled={submitting}
            />
            <p className="mt-1 text-xs text-slate-500">Use at least 8 characters to keep your account secure.</p>
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-slate-700">
              Confirm password
            </label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="••••••••"
              className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-100"
              autoComplete="new-password"
              minLength={8}
              disabled={submitting}
            />
          </div>

          {errorMessage && (
            <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700" role="alert">
              {errorMessage}
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={handleSkip}
              disabled={submitting}
              className="flex-1 rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Skip for now
            </button>
            <button
              type="submit"
              disabled={submitting || !password || !confirmPassword}
              className="flex-1 rounded-xl bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-primary-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {submitting ? 'Setting password...' : 'Set password'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
