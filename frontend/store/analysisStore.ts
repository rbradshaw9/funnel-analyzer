import { create } from 'zustand'
import { AnalysisResult } from '@/types'

interface AnalysisStore {
  currentAnalysis: AnalysisResult | null
  isAnalyzing: boolean
  setCurrentAnalysis: (analysis: AnalysisResult | null) => void
  setAnalyzing: (analyzing: boolean) => void
}

export const useAnalysisStore = create<AnalysisStore>((set) => ({
  currentAnalysis: null,
  isAnalyzing: false,
  setCurrentAnalysis: (analysis) => set({ currentAnalysis: analysis }),
  setAnalyzing: (analyzing) => set({ isAnalyzing: analyzing }),
}))
