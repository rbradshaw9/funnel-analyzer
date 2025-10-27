import axios from 'axios'
import {
  AnalysisResult,
  AdminLoginResponse,
  AuthResponse,
  MagicLinkResponse,
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
  token?: string | null
}

interface ReportListOptions {
  limit?: number
  offset?: number
  token?: string | null
}

interface ReportDetailOptions {
  token?: string | null
}

interface DeleteReportOptions {
  token?: string | null
}

const authHeaders = (token?: string | null) =>
  token ? { Authorization: `Bearer ${token}` } : undefined

export async function analyzeFunnel(urls: string[], options: AnalyzeFunnelOptions = {}): Promise<AnalysisResult> {
  try {
    const payload: Record<string, unknown> = { urls }

    if (options.email) {
      payload.email = options.email
    }

    const response = await api.post<AnalysisResult>('/api/analyze', payload, {
      headers: authHeaders(options.token),
    })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to analyze funnel')
  }
}

export async function validateToken(token: string): Promise<AuthResponse> {
  try {
    const response = await api.post<AuthResponse>('/api/auth/validate', { token })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to validate token')
  }
}

export async function getReports(options: ReportListOptions = {}): Promise<ReportListResponse> {
  try {
    const { limit = 10, offset = 0, token } = options

    const response = await api.get<ReportListResponse>('/api/reports', {
      params: { limit, offset },
      headers: authHeaders(token),
    })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch reports')
  }
}

export async function getReportDetail(
  analysisId: number,
  options: ReportDetailOptions = {},
): Promise<AnalysisResult> {
  try {
    const response = await api.get<AnalysisResult>(`/api/reports/detail/${analysisId}`, {
      headers: authHeaders(options.token),
    })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch report detail')
  }
}

export async function deleteReport(
  analysisId: number,
  options: DeleteReportOptions = {},
): Promise<ReportDeleteResponse> {
  try {
    const response = await api.delete<ReportDeleteResponse>(`/api/reports/detail/${analysisId}`, {
      headers: authHeaders(options.token),
    })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to delete report')
  }
}

export async function sendAnalysisEmail(analysisId: number, email: string, token?: string | null): Promise<void> {
  try {
    await api.post(
      `/api/analyze/${analysisId}/email`,
      { email },
      { headers: authHeaders(token) },
    )
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

export async function adminLogin(email: string, password: string): Promise<AdminLoginResponse> {
  try {
    const response = await api.post<AdminLoginResponse>('/api/auth/admin/login', { email, password })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Invalid credentials')
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
