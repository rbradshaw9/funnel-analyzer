import axios from 'axios'
import {
  AnalysisResult,
  AdminLoginResponse,
  AuthResponse,
  MagicLinkResponse,
  ReportDeleteResponse,
  ReportListResponse,
} from '@/types'

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://analyzer.smarttoolclub.com'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

interface AnalyzeFunnelOptions {
  email?: string
  userId?: number | null
}

export async function analyzeFunnel(urls: string[], options: AnalyzeFunnelOptions = {}): Promise<AnalysisResult> {
  try {
    const payload: Record<string, unknown> = { urls }

    if (options.email) {
      payload.email = options.email
    }

    const params: Record<string, number> = {}
    if (typeof options.userId === 'number') {
      params.user_id = options.userId
    }

    const response = await api.post<AnalysisResult>('/api/analyze', payload, { params })
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

export async function adminLogin(email: string, password: string): Promise<AdminLoginResponse> {
  try {
    const response = await api.post<AdminLoginResponse>('/api/auth/admin/login', { email, password })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Invalid credentials')
  }
}
