export interface ScoreBreakdown {
  clarity: number
  value: number
  proof: number
  design: number
  flow: number
}

export interface PageAnalysis {
  url: string
  page_type?: string
  title?: string
  scores: ScoreBreakdown
  feedback: string
  screenshot_url?: string
}

export interface AnalysisResult {
  analysis_id: number
  overall_score: number
  scores: ScoreBreakdown
  summary: string
  pages: PageAnalysis[]
  created_at: string
  analysis_duration_seconds?: number
}

export interface AuthResponse {
  valid: boolean
  user_id?: number
  email?: string
  message?: string
}
