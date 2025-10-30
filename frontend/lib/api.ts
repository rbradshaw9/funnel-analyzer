import axios from 'axios'
import type {
  AnalysisResult,
  AdminLoginResponse,
  AuthCredentialsResponse,
  AuthResponse,
  LoginPayload,
  MagicLinkResponse,
  RegisterPayload,
  ReportDeleteResponse,
  ReportListResponse,
  PublicStatsResponse,
} from '@/types'

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.funnelanalyzerpro.com'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

interface AnalyzeFunnelOptions {
  email?: string
  userId?: number | null
  token?: string | null
  industry?: string
  name?: string
  parentAnalysisId?: number
  onProgress?: (progress: ProgressUpdate) => void
}

export interface ProgressUpdate {
  analysis_id: string
  stage: string
  progress_percent: number
  message: string
  current_page?: number | null
  total_pages?: number | null
  timestamp?: string
}

export async function analyzeFunnel(urls: string[], options: AnalyzeFunnelOptions = {}): Promise<AnalysisResult> {
  try {
    const payload: Record<string, unknown> = { urls }

    if (options.email) {
      payload.email = options.email
    }

    if (options.industry) {
      payload.industry = options.industry
    }

    if (options.name) {
      payload.name = options.name
    }

    if (options.parentAnalysisId) {
      payload.parent_analysis_id = options.parentAnalysisId
    }

    const params: Record<string, number> = {}
    if (typeof options.userId === 'number') {
      params.user_id = options.userId
    }

    const headers: Record<string, string> = {}
    if (options.token) {
      headers.Authorization = `Bearer ${options.token}`
    }

    // Start the analysis request
    // Note: This is a blocking call that won't return until analysis is complete
    const response = await api.post<AnalysisResult>('/api/analyze', payload, {
      params,
      headers: Object.keys(headers).length > 0 ? headers : undefined,
    })

    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to analyze funnel')
  }
}

export async function getAnalysisProgress(analysisId: string): Promise<ProgressUpdate> {
  const response = await api.get<ProgressUpdate>(`/api/analysis/progress/${analysisId}`)
  return response.data
}

export async function validateToken(token: string): Promise<AuthResponse> {
  try {
    const response = await api.post<AuthResponse>('/api/auth/validate', { token })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to validate token')
  }
}

export async function getReports(userId: number, limit = 10, offset = 0): Promise<ReportListResponse> {
  try {
    const response = await api.get<ReportListResponse>(`/api/reports/${userId}`, {
      params: { limit, offset },
    })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch reports')
  }
}

interface ReportDetailOptions {
  userId?: number
}

export async function getReportDetail(
  analysisId: number,
  options: ReportDetailOptions = {},
): Promise<AnalysisResult> {
  try {
    const params: Record<string, number> = {}
    if (typeof options.userId === 'number') {
      params.user_id = options.userId
    }

    const response = await api.get<AnalysisResult>(`/api/reports/detail/${analysisId}`, {
      params,
    })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch report detail')
  }
}

interface DeleteReportOptions {
  userId?: number
}

export async function deleteReport(
  analysisId: number,
  options: DeleteReportOptions = {},
): Promise<ReportDeleteResponse> {
  try {
    const params: Record<string, number> = {}
    if (typeof options.userId === 'number') {
      params.user_id = options.userId
    }

    const response = await api.delete<ReportDeleteResponse>(`/api/reports/detail/${analysisId}`, {
      params,
    })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to delete report')
  }
}

export async function sendAnalysisEmail(analysisId: number, email: string): Promise<void> {
  try {
    await api.post(`/api/analyze/${analysisId}/email`, { email })
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to send analysis email')
  }
}

export async function requestMagicLink(email: string): Promise<MagicLinkResponse> {
  try {
    const response = await api.post<MagicLinkResponse>('/api/auth/magic-link', { email })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to send magic link')
  }
}

export async function registerAccount(payload: RegisterPayload): Promise<AuthCredentialsResponse> {
  try {
    const response = await api.post<any>('/api/auth/register', payload)
    // Backend returns access_token, but frontend expects token
    return {
      token: response.data.access_token,
      refresh_token: response.data.refresh_token,
      expires_at: response.data.expires_in ? new Date(Date.now() + response.data.expires_in * 1000).toISOString() : null,
      user_id: response.data.user_id,
      email: response.data.email,
    }
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to create account')
  }
}

export async function loginAccount(email: string, password: string): Promise<AuthCredentialsResponse> {
  try {
    const payload: LoginPayload = { email, password }
    const response = await api.post<any>('/api/auth/login', payload)
    // Backend returns access_token, but frontend expects token
    return {
      token: response.data.access_token,
      refresh_token: response.data.refresh_token,
      expires_at: response.data.expires_in ? new Date(Date.now() + response.data.expires_in * 1000).toISOString() : null,
      user_id: response.data.user_id,
      email: response.data.email,
    }
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Invalid email or password')
  }
}

export async function adminLogin(email: string, password: string): Promise<AdminLoginResponse> {
  try {
    const response = await api.post<AdminLoginResponse>('/api/auth/admin/login', { email, password })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Invalid credentials')
  }
}

export async function refreshAccessToken(refreshToken: string): Promise<AuthCredentialsResponse> {
  try {
    const response = await api.post<AuthCredentialsResponse>('/api/auth/refresh', { 
      refresh_token: refreshToken 
    })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to refresh token')
  }
}

export async function setUserPassword(token: string, password: string): Promise<{ status: string; message: string }> {
  try {
    const response = await api.post<{ status: string; message: string }>(
      '/api/auth/set-password',
      { password },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    )
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to set password')
  }
}

export interface UpdateProfilePayload {
  full_name?: string
  company?: string
  job_title?: string
  onboarding_completed?: boolean
}

export interface ProfileResponse {
  user_id: number
  email: string
  full_name?: string | null
  company?: string | null
  job_title?: string | null
  avatar_url?: string | null
  onboarding_completed: boolean
  plan: string
  status: string
}

export async function getUserProfile(token: string): Promise<ProfileResponse> {
  try {
    const response = await api.get<ProfileResponse>('/api/user/profile', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch profile')
  }
}

export async function updateUserProfile(token: string, payload: UpdateProfilePayload): Promise<ProfileResponse> {
  try {
    const response = await api.patch<ProfileResponse>('/api/user/profile', payload, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to update profile')
  }
}

export async function getPublicStats(): Promise<PublicStatsResponse> {
  try {
    const response = await api.get<PublicStatsResponse>('/api/metrics/stats')
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to load public stats')
  }
}

// Analysis naming and versioning
export async function renameAnalysis(analysisId: number, name: string, userId?: number): Promise<{ status: string; analysis_id: number; name: string }> {
  try {
    const params: Record<string, number> = {}
    if (typeof userId === 'number') {
      params.user_id = userId
    }

    const response = await api.patch(`/api/reports/detail/${analysisId}/rename`, 
      { name },
      { params }
    )
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to rename analysis')
  }
}

export interface AnalysisVersion {
  analysis_id: number
  version: number
  name?: string
  overall_score: number
  created_at: string
  is_current: boolean
  parent_analysis_id?: number
}

export interface AnalysisVersionsResponse {
  versions: AnalysisVersion[]
  count: number
}

export async function getAnalysisVersions(analysisId: number, userId?: number): Promise<AnalysisVersionsResponse> {
  try {
    const params: Record<string, number> = {}
    if (typeof userId === 'number') {
      params.user_id = userId
    }

    const response = await api.get<AnalysisVersionsResponse>(`/api/reports/detail/${analysisId}/versions`, { params })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch analysis versions')
  }
}

export async function initiateRerun(analysisId: number, userId?: number): Promise<{ status: string; urls: string[]; parent_analysis_id: number }> {
  try {
    const params: Record<string, number> = {}
    if (typeof userId === 'number') {
      params.user_id = userId
    }

    const response = await api.post(`/api/reports/detail/${analysisId}/rerun`, {}, { params })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to initiate rerun')
  }
}
