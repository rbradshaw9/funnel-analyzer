"use client"

import { useEffect, useRef, useState } from 'react'
import { requestMagicLink, adminLogin, exchangeAuth0Code } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'

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
  const auth0HandledRef = useRef(false)
  const { setToken, setAuth, setError: setAuthStoreError } = useAuthStore()

  const auth0Domain = process.env.NEXT_PUBLIC_AUTH0_DOMAIN
  const auth0ClientId = process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID
  const auth0Configured = Boolean(auth0Domain && auth0ClientId)

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

  const handleAuth0Login = () => {
    setStatusMessage(null)
    setErrorMessage(null)

    if (!auth0Configured) {
      setErrorMessage('Auth0 login is not configured.')
      return
    }

    let redirectUri = process.env.NEXT_PUBLIC_AUTH0_REDIRECT_URI
    if (!redirectUri && typeof window !== 'undefined') {
      redirectUri = `${window.location.origin}/auth/callback`
    }

    if (!redirectUri) {
      setErrorMessage('Auth0 redirect URI is missing.')
      return
    }

    const stateValue = typeof window !== 'undefined' && window.crypto?.randomUUID
      ? `auth0-${window.crypto.randomUUID()}`
      : `auth0-${Math.random().toString(36).slice(2)}`

    if (typeof window !== 'undefined') {
      window.sessionStorage.setItem('auth0_oauth_state', stateValue)
    }

    const params = new URLSearchParams({
      client_id: auth0ClientId!,
      response_type: 'code',
      scope: 'openid profile email',
      redirect_uri: redirectUri,
      state: stateValue,
    })

    const authorizeUrl = `https://${auth0Domain}/authorize?${params.toString()}`
    if (typeof window !== 'undefined') {
      window.location.href = authorizeUrl
    }
  }

  useEffect(() => {
    if (typeof window === 'undefined') {
      return
    }

    const params = new URLSearchParams(window.location.search)
    const code = params.get('code')
    const state = params.get('state')
    const storedState = window.sessionStorage.getItem('auth0_oauth_state')

    if (!code || !state) {
      return
    }

    if (!storedState) {
      return
    }

    if (state !== storedState) {
      window.sessionStorage.removeItem('auth0_oauth_state')
      setErrorMessage('Login verification failed. Please try again.')
      return
    }

    if (auth0HandledRef.current) {
      return
    }
    auth0HandledRef.current = true

    const redirectUri = process.env.NEXT_PUBLIC_AUTH0_REDIRECT_URI || `${window.location.origin}/auth/callback`

    const completeLogin = async () => {
      setSubmitting(true)
      setStatusMessage('Signing you in…')
      setErrorMessage(null)

      try {
        const oauth = await exchangeAuth0Code(code, redirectUri)
        setToken(oauth.access_token)
        setAuth(null)
        setAuthStoreError(null)
        window.sessionStorage.removeItem('auth0_oauth_state')

        const cleanedUrl = new URL(window.location.href)
        cleanedUrl.searchParams.delete('code')
        cleanedUrl.searchParams.delete('state')
        window.history.replaceState({}, document.title, cleanedUrl.toString())

        window.location.href = `/dashboard?token=${encodeURIComponent(oauth.access_token)}`
      } catch (error: any) {
        window.sessionStorage.removeItem('auth0_oauth_state')
        setStatusMessage(null)
        setErrorMessage(error?.message || 'Unable to complete Auth0 login.')
      } finally {
        setSubmitting(false)
      }
    }

    void completeLogin()
  }, [setAuth, setAuthStoreError, setErrorMessage, setStatusMessage, setSubmitting, setToken])

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
              <div className="mt-4 space-y-4">
                {auth0Configured && (
                  <div className="space-y-3">
                    <button
                      type="button"
                      onClick={handleAuth0Login}
                      className="flex w-full items-center justify-center gap-2 rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        aria-hidden="true"
                        className="h-4 w-4 text-[#eb5424]"
                      >
                        <path
                          fill="currentColor"
                          d="M19.23 7.51h-3.69L12 0l-3.54 7.51H4.77L8.31 12l-3.54 4.49h3.69L12 24l3.54-7.51h3.69L15.69 12l3.54-4.49z"
                        />
                      </svg>
                      Continue with Auth0
                    </button>
                    <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
                      <span className="h-px flex-1 bg-slate-200" />
                      <span>Or email</span>
                      <span className="h-px flex-1 bg-slate-200" />
                    </div>
                  </div>
                )}

                <form className="space-y-4" onSubmit={handleMagicSubmit}>
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
              </div>
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
