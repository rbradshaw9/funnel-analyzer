export interface ScoreBreakdown {
  clarity: number
  value: number
  proof: number
  design: number
  flow: number
}

export interface CTARecommendation {
  copy: string
  location?: string
  reason?: string
}

export interface DesignImprovement {
  area?: string
  recommendation: string
  impact?: string
}

export interface TrustElementRecommendation {
  element: string
  why?: string
}

export interface ABTestPlan {
  element?: string
  control?: string
  variant?: string
  expected_lift?: string
  reasoning?: string
}

export interface PriorityAlert {
  severity?: string
  issue: string
  impact?: string
  fix?: string
}

export interface FunnelFlowGap {
  step?: string
  issue: string
  fix?: string
}

export interface CopyDiagnostics {
  hook?: string
  offer?: string
  urgency?: string
  objections?: string
  audience_fit?: string
}

export interface VisualDiagnostics {
  hero?: string
  layout?: string
  contrast?: string
  mobile?: string
  credibility?: string
}

export interface VideoRecommendation {
  context?: string
  recommendation: string
}

export interface PageAnalysis {
  url: string
  page_type?: string
  title?: string
  scores: ScoreBreakdown
  feedback: string
  screenshot_url?: string
  headline_recommendation?: string
  cta_recommendations?: CTARecommendation[]
  design_improvements?: DesignImprovement[]
  trust_elements_missing?: TrustElementRecommendation[]
  ab_test_priority?: ABTestPlan
  priority_alerts?: PriorityAlert[]
  funnel_flow_gaps?: FunnelFlowGap[]
  copy_diagnostics?: CopyDiagnostics
  visual_diagnostics?: VisualDiagnostics
  video_recommendations?: VideoRecommendation[]
  email_capture_recommendations?: string[]
}

export interface AnalysisResult {
  analysis_id: number
  overall_score: number
  scores: ScoreBreakdown
  summary: string
  pages: PageAnalysis[]
  created_at: string
  analysis_duration_seconds?: number
  recipient_email?: string
}

export interface AuthResponse {
  valid: boolean
  user_id?: number
  email?: string
  message?: string
}
