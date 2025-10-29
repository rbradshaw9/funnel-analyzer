'use client'

import { Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'

function AuthErrorContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const errorMessage = searchParams.get('message') || 'An unexpected error occurred during authentication'

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 px-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-xl">
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-rose-100">
          <svg className="h-8 w-8 text-rose-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" 
            />
          </svg>
        </div>
        
        <h1 className="text-2xl font-bold text-slate-900">Authentication Error</h1>
        
        <p className="mt-3 text-sm text-slate-600">
          {decodeURIComponent(errorMessage)}
        </p>

        <div className="mt-6 flex flex-col gap-3">
          <button
            onClick={() => router.push('/dashboard')}
            className="rounded-xl bg-primary-600 px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-primary-700"
          >
            Try Again
          </button>
          
          <button
            onClick={() => router.push('/')}
            className="text-sm text-slate-600 transition hover:text-slate-900"
          >
            Return to Home
          </button>
        </div>

        <p className="mt-6 text-xs text-slate-400">
          If this problem persists, please contact support at support@funnelanalyzerpro.com
        </p>
      </div>
    </div>
  )
}

export default function AuthErrorPage() {
  return (
    <Suspense fallback={
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
        <div className="h-16 w-16 animate-spin rounded-full border-4 border-slate-200 border-t-primary-600" />
      </div>
    }>
      <AuthErrorContent />
    </Suspense>
  )
}
