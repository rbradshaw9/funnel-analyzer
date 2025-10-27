'use client'

import { useEffect, useRef, useState } from 'react'

import { loginAccount, registerAccount } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'
import type { AuthCredentialsResponse } from '@/types'

export type AuthMode = 'signup' | 'login'

interface AuthModalProps {
  open: boolean
  onClose: () => void
  defaultMode?: AuthMode
  onAuthenticated?: (response: AuthCredentialsResponse) => void
}

const NAME_PLACEHOLDER = 'Taylor Johnson'
const EMAIL_PLACEHOLDER = 'taylor@example.com'

export function AuthModal({ open, onClose, defaultMode = 'signup', onAuthenticated }: AuthModalProps) {
  const [mode, setMode] = useState<AuthMode>(defaultMode)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const setToken = useAuthStore((state) => state.setToken)
  const setError = useAuthStore((state) => state.setError)

  const successTimeout = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    if (!open) {
      return
    }
    setMode(defaultMode)
    setSuccessMessage(null)
    setErrorMessage(null)
  }, [defaultMode, open])

  useEffect(() => () => {
    if (successTimeout.current) {
      clearTimeout(successTimeout.current)
      successTimeout.current = null
    }
  }, [])

  if (!open) {
    return null
  }

  const resetForm = () => {
    setName('')
    setEmail('')
    setPassword('')
    setSuccessMessage(null)
    setErrorMessage(null)
    setSubmitting(false)
  }

  const handleClose = () => {
    if (successTimeout.current) {
      clearTimeout(successTimeout.current)
      successTimeout.current = null
    }
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
    const normalizedName = name.trim()

    try {
      let response: AuthCredentialsResponse

      if (mode === 'signup') {
        response = await registerAccount({
          email: normalizedEmail,
          password,
          name: normalizedName || undefined,
        })
      } else {
        response = await loginAccount(normalizedEmail, password)
      }

      if (!response.token) {
        setErrorMessage('We could not verify your session token. Please try again.')
        return
      }

      setToken(response.token)
      setError(null)

      const message = mode === 'signup' ? 'Account created! Unlocking your report…' : 'Welcome back! Unlocking your report…'
      setSuccessMessage(message)

      successTimeout.current = setTimeout(() => {
        onAuthenticated?.(response)
        handleClose()
      }, 1200)
    } catch (error: any) {
      setErrorMessage(error?.message || 'We could not process your request. Please try again.')
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
          {mode === 'signup' && (
            <div>
              <label htmlFor="auth-name" className="block text-sm font-semibold text-slate-700">
                Full name
              </label>
              <input
                id="auth-name"
                type="text"
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder={NAME_PLACEHOLDER}
                className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-100"
                autoComplete="name"
              />
            </div>
          )}

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
              autoComplete={mode === 'login' ? 'email' : 'username'}
            />
          </div>

          <div>
            <label htmlFor="auth-password" className="block text-sm font-semibold text-slate-700">
              Password
            </label>
            <input
              id="auth-password"
              type="password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="••••••••"
              className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-100"
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              minLength={8}
            />
            {mode === 'signup' && (
              <p className="mt-1 text-xs text-slate-500">Use at least 8 characters to keep your account secure.</p>
            )}
          </div>

          <button
            type="submit"
            className="w-full rounded-xl bg-gradient-to-r from-primary-600 to-accent-500 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:from-primary-700 hover:to-accent-600 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={submitting || Boolean(successMessage)}
          >
            {submitting
              ? mode === 'signup'
                ? 'Creating account…'
                : 'Logging in…'
              : mode === 'signup'
                ? 'Create free account'
                : 'Log in'}
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
