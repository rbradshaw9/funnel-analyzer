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

export interface PipelineStageTimings {
  scrape_seconds?: number
  analysis_seconds?: number
  screenshot_seconds?: number
  total_seconds?: number
}

export interface ScreenshotPipelineMetrics {
  attempted: number
  succeeded: number
  failed: number
  uploaded: number
  timeouts: number
}

export interface PipelineTelemetry {
  stage_timings?: PipelineStageTimings
  screenshot?: ScreenshotPipelineMetrics
  llm_provider?: string
  notes?: string[]
}

export interface PageAnalysis {
  url: string
  page_type?: string
  title?: string
  scores: ScoreBreakdown
  feedback: string
  screenshot_url?: string
  screenshot_storage_key?: string
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
  pipeline_metrics?: PipelineTelemetry
}

export interface ReportListItem {
  analysis_id: number
  overall_score: number
  urls: string[]
  created_at: string
}

export interface ReportListResponse {
  reports: ReportListItem[]
  total: number
}

export interface ReportDeleteResponse {
  status: 'deleted'
  analysis_id: number
  assets_total: number
  assets_deleted: number
  assets_failed: number
  assets_skipped: number
  storage_available: boolean
}

export interface AuthResponse {
  valid: boolean
  user_id?: number
  email?: string
  message?: string
  plan?: string
  status?: string
  status_reason?: string
  access_granted?: boolean
  access_expires_at?: string
  portal_update_url?: string
  token_type?: string
  expires_at?: string
}

export interface MagicLinkResponse {
  status: 'sent' | 'skipped'
  message?: string
}

export interface AdminLoginResponse {
  access_token: string
  token_type: 'bearer'
  expires_in?: number
}

export interface PublicStatsResponse {
  analyses_run: number
  pages_analyzed: number
}
