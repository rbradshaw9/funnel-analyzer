import { create } from 'zustand'
import type { AuthResponse } from '@/types'

type AuthError = string | null

interface AuthState {
  token: string | null
  auth: AuthResponse | null
  loading: boolean
  error: AuthError
  setToken: (token: string | null) => void
  setAuth: (auth: AuthResponse | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: AuthError) => void
  reset: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  auth: null,
  loading: false,
  error: null,
  setToken: (token) => set({ token }),
  setAuth: (auth) => set({ auth }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  reset: () => set({ token: null, auth: null, loading: false, error: null }),
}))
