'use client'

import { useEffect, useState } from 'react'

import { validateToken } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'
import type { AuthResponse } from '@/types'

interface AuthValidationResult {
  token: string | null
  loading: boolean
  error: string | null
  authStatus: string | null
  statusMessage: string | null
  statusReason: string | null
  portalUrl: string | null
  accessGranted: boolean
  isLocked: boolean
  auth: AuthResponse | null
  userId: number | null
}

export function useAuthValidation(): AuthValidationResult {
  const [tokenFromQuery, setTokenFromQuery] = useState<string | null>(null)

  const token = useAuthStore((state) => state.token)
  const auth = useAuthStore((state) => state.auth)
  const loading = useAuthStore((state) => state.loading)
  const error = useAuthStore((state) => state.error)
  const hydrate = useAuthStore((state) => state.hydrate)
  const setToken = useAuthStore((state) => state.setToken)
  const setAuth = useAuthStore((state) => state.setAuth)
  const setLoading = useAuthStore((state) => state.setLoading)
  const setError = useAuthStore((state) => state.setError)

  useEffect(() => {
    hydrate()
  }, [hydrate])

  useEffect(() => {
    if (typeof window === 'undefined') {
      return
    }

    try {
      const params = new URLSearchParams(window.location.search)
      const queryToken = params.get('token')
      setTokenFromQuery(queryToken)
    } catch (error) {
      console.warn('Failed to read auth token from URL search params', error)
      setTokenFromQuery(null)
    }
  }, [])

  useEffect(() => {
    if (!tokenFromQuery) {
      return
    }
    const current = useAuthStore.getState().token
    if (current === tokenFromQuery) {
      return
    }
    setToken(tokenFromQuery)
  }, [tokenFromQuery, setToken])

  useEffect(() => {
    if (!token) {
      setAuth(null)
      setError(null)
      setLoading(false)
      return
    }

    let cancelled = false

    const run = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await validateToken(token)
        if (!cancelled) {
          setAuth(response)
        }
      } catch (err: any) {
        if (!cancelled) {
          setAuth(null)
          setError(err?.message || 'Unable to validate membership token.')
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void run()

    return () => {
      cancelled = true
    }
  }, [token, setAuth, setError, setLoading])

  const accessGranted = !token || Boolean(auth?.access_granted)

  let authStatus: string | null = null
  if (auth) {
    const plan = auth.plan?.trim()
    const status = auth.status?.replace(/_/g, ' ').trim()
    if (plan && status) {
      authStatus = `${plan} · ${status}`
    } else if (plan || status) {
      authStatus = (plan || status) ?? null
    }
  }

  const isLocked = token ? (!auth || !accessGranted) : false

  return {
    token,
    loading,
    error,
    authStatus,
    statusMessage: auth?.message ?? null,
    statusReason: auth?.status_reason ?? null,
    portalUrl: auth?.portal_update_url ?? null,
    accessGranted,
    isLocked,
    auth,
    userId: auth?.user_id ?? null,
  }
}
