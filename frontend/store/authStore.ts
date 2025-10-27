import { create } from 'zustand'
import type { AuthResponse } from '@/types'

type AuthError = string | null

const TOKEN_STORAGE_KEY = 'faAuthToken'
const REFRESH_TOKEN_STORAGE_KEY = 'faRefreshToken'

const readStoredToken = (): string | null => {
  if (typeof window === 'undefined') {
    return null
  }
  try {
    return window.localStorage.getItem(TOKEN_STORAGE_KEY)
  } catch (error) {
    console.warn('Failed to read auth token from storage', error)
    return null
  }
}

const readStoredRefreshToken = (): string | null => {
  if (typeof window === 'undefined') {
    return null
  }
  try {
    return window.localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY)
  } catch (error) {
    console.warn('Failed to read refresh token from storage', error)
    return null
  }
}

const persistToken = (token: string | null) => {
  if (typeof window === 'undefined') {
    return
  }
  try {
    if (token) {
      window.localStorage.setItem(TOKEN_STORAGE_KEY, token)
    } else {
      window.localStorage.removeItem(TOKEN_STORAGE_KEY)
    }
  } catch (error) {
    console.warn('Failed to persist auth token', error)
  }
}

const persistRefreshToken = (refreshToken: string | null) => {
  if (typeof window === 'undefined') {
    return
  }
  try {
    if (refreshToken) {
      window.localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, refreshToken)
    } else {
      window.localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY)
    }
  } catch (error) {
    console.warn('Failed to persist refresh token', error)
  }
}

interface AuthState {
  token: string | null
  refreshToken: string | null
  auth: AuthResponse | null
  loading: boolean
  error: AuthError
  hydrate: () => void
  setToken: (token: string | null) => void
  setRefreshToken: (refreshToken: string | null) => void
  setTokens: (token: string | null, refreshToken: string | null) => void
  setAuth: (auth: AuthResponse | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: AuthError) => void
  reset: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: typeof window === 'undefined' ? null : readStoredToken(),
  refreshToken: typeof window === 'undefined' ? null : readStoredRefreshToken(),
  auth: null,
  loading: false,
  error: null,
  hydrate: () => {
    const stored = readStoredToken()
    const storedRefresh = readStoredRefreshToken()
    set({ token: stored, refreshToken: storedRefresh })
  },
  setToken: (token) => {
    persistToken(token)
    set({ token })
  },
  setRefreshToken: (refreshToken) => {
    persistRefreshToken(refreshToken)
    set({ refreshToken })
  },
  setTokens: (token, refreshToken) => {
    persistToken(token)
    persistRefreshToken(refreshToken)
    set({ token, refreshToken })
  },
  setAuth: (auth) => set({ auth }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  reset: () => {
    persistToken(null)
    persistRefreshToken(null)
    set({ token: null, refreshToken: null, auth: null, loading: false, error: null })
  },
}))

export { TOKEN_STORAGE_KEY, REFRESH_TOKEN_STORAGE_KEY }
