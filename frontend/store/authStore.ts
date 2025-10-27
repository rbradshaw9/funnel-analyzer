import { create } from 'zustand'
import type { AuthResponse } from '@/types'

type AuthError = string | null

const TOKEN_STORAGE_KEY = 'faAuthToken'

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

interface AuthState {
  token: string | null
  auth: AuthResponse | null
  loading: boolean
  error: AuthError
  hydrate: () => void
  setToken: (token: string | null) => void
  setAuth: (auth: AuthResponse | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: AuthError) => void
  reset: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: typeof window === 'undefined' ? null : readStoredToken(),
  auth: null,
  loading: false,
  error: null,
  hydrate: () => {
    const stored = readStoredToken()
    set({ token: stored })
  },
  setToken: (token) => {
    persistToken(token)
    set({ token })
  },
  setAuth: (auth) => set({ auth }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  reset: () => {
    persistToken(null)
    set({ token: null, auth: null, loading: false, error: null })
  },
}))

export { TOKEN_STORAGE_KEY }
