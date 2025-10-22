'use client'

import { motion } from 'framer-motion'

interface Props {
  label: string
  score: number
}

export default function ScoreCard({ label, score }: Props) {
  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600 bg-green-50 border-green-200'
    if (score >= 75) return 'text-blue-600 bg-blue-50 border-blue-200'
    if (score >= 60) return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    return 'text-red-600 bg-red-50 border-red-200'
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className={`p-4 rounded-xl border-2 ${getScoreColor(score)}`}
    >
      <div className="text-sm font-medium mb-1">{label}</div>
      <div className="text-3xl font-bold">{score}</div>
      <div className="text-xs opacity-70">/100</div>
    </motion.div>
  )
}
