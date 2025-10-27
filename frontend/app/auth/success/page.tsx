'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'

export default function AuthSuccessPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing')
  const setTokens = useAuthStore((state) => state.setTokens)

  useEffect(() => {
    const token = searchParams.get('token')
    
    if (!token) {
      setStatus('error')
      return
    }

    try {
      // Store the access token (refresh token was already stored by backend in cookie or will come separately)
      setTokens(token, null)
      setStatus('success')
      
      // Redirect to dashboard after a brief moment
      setTimeout(() => {
        router.push('/dashboard')
      }, 1500)
    } catch (error) {
      console.error('Failed to process OAuth callback:', error)
      setStatus('error')
    }
  }, [searchParams, setTokens, router])

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 px-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-xl">
        {status === 'processing' && (
          <>
            <div className="mx-auto mb-4 h-16 w-16 animate-spin rounded-full border-4 border-slate-200 border-t-primary-600" />
            <h1 className="text-2xl font-bold text-slate-900">Completing sign in...</h1>
            <p className="mt-2 text-sm text-slate-600">Please wait while we set up your account</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100">
              <svg className="h-8 w-8 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-slate-900">Welcome!</h1>
            <p className="mt-2 text-sm text-slate-600">Redirecting you to your dashboard...</p>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-rose-100">
              <svg className="h-8 w-8 text-rose-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-slate-900">Authentication Failed</h1>
            <p className="mt-2 text-sm text-slate-600">We couldn't complete your sign in. Please try again.</p>
            <button
              onClick={() => router.push('/dashboard')}
              className="mt-6 rounded-xl bg-primary-600 px-6 py-2 text-sm font-semibold text-white transition hover:bg-primary-700"
            >
              Return to Dashboard
            </button>
          </>
        )}
      </div>
    </div>
  )
}
