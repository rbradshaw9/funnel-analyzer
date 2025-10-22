import axios from 'axios'
import { AnalysisResult, AuthResponse } from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://funnel-analyzer-production-b6b4.up.railway.app'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export async function analyzeFunnel(urls: string[]): Promise<AnalysisResult> {
  try {
    const response = await api.post<AnalysisResult>('/api/analyze', { urls })
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

export async function getReports(userId: number, limit = 10, offset = 0): Promise<any> {
  try {
    const response = await api.get(`/api/reports/${userId}`, {
      params: { limit, offset },
    })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch reports')
  }
}

export async function getReportDetail(analysisId: number): Promise<AnalysisResult> {
  try {
    const response = await api.get<AnalysisResult>(`/api/reports/detail/${analysisId}`)
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch report detail')
  }
}
