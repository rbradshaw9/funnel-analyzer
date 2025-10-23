'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { FiPlus, FiX } from 'react-icons/fi'
import { useAnalysisStore } from '@/store/analysisStore'
import { analyzeFunnel } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'

const LOCK_MESSAGE = 'Your membership is inactive. Update billing to run a new analysis.'

interface URLInputFormProps {
  isLocked?: boolean
}

export default function URLInputForm({ isLocked = false }: URLInputFormProps) {
  const [urls, setUrls] = useState<string[]>([''])
  const [error, setError] = useState<string>('')
  const [recipientEmail, setRecipientEmail] = useState<string>('')
  const { setAnalyzing, setCurrentAnalysis } = useAnalysisStore()
  const auth = useAuthStore((state) => state.auth)

  useEffect(() => {
    if (!isLocked && error === LOCK_MESSAGE) {
      setError('')
    }
  }, [isLocked, error])

  const addUrlField = () => {
    if (urls.length < 10) {
      setUrls([...urls, ''])
      setError('')
    }
  }

  const removeUrlField = (index: number) => {
    if (urls.length > 1) {
      setUrls(urls.filter((_, i) => i !== index))
    }
  }

  const updateUrl = (index: number, value: string) => {
    const newUrls = [...urls]
    newUrls[index] = value
    setUrls(newUrls)
    setError('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (isLocked) {
      setError(LOCK_MESSAGE)
      return
    }

    // Filter out empty URLs
    const validUrls = urls.filter(url => url.trim() !== '')
    
    if (validUrls.length === 0) {
      setError('Please enter at least one URL')
      return
    }

    // Validate URLs
    const urlPattern = /^https?:\/\/.+/
    const invalidUrls = validUrls.filter(url => !urlPattern.test(url))
    
    if (invalidUrls.length > 0) {
      setError('Please enter valid URLs starting with http:// or https://')
      return
    }

    const trimmedEmail = recipientEmail.trim()
    if (trimmedEmail && !/^\S+@\S+\.\S+$/.test(trimmedEmail)) {
      setError('Please enter a valid email address')
      return
    }

    try {
      setAnalyzing(true)
      setError('')
      
      const result = await analyzeFunnel(validUrls, {
        email: trimmedEmail || undefined,
        userId: auth?.user_id ?? undefined,
      })
      setCurrentAnalysis(result)
    } catch (err: any) {
      setError(err.message || 'Failed to analyze funnel. Please try again.')
    } finally {
      setAnalyzing(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl shadow-soft-lg p-8"
    >
      <form onSubmit={handleSubmit}>
        {isLocked && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-4 rounded-lg border border-amber-200 bg-amber-50 p-4 text-amber-800"
          >
            {LOCK_MESSAGE}
          </motion.div>
        )}
        <div className="space-y-4">
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Enter Funnel URLs (max 10)
          </label>
          
          {urls.map((url, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className="flex gap-2"
            >
              <input
                type="text"
                value={url}
                onChange={(e) => updateUrl(index, e.target.value)}
                placeholder={`URL ${index + 1} (e.g., https://example.com/sales)`}
                className="flex-1 px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all"
              />
              {urls.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeUrlField(index)}
                  className="px-3 py-3 text-slate-400 hover:text-red-500 transition-colors"
                  aria-label="Remove URL"
                >
                  <FiX className="text-xl" />
                </button>
              )}
            </motion.div>
          ))}
        </div>

        {urls.length < 10 && (
          <button
            type="button"
            onClick={addUrlField}
            className="mt-4 flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium transition-colors"
          >
            <FiPlus /> Add Another URL
          </button>
        )}

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg"
          >
            {error}
          </motion.div>
        )}

        <div className="mt-6">
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Optional: Email results to this address
          </label>
          <input
            type="email"
            value={recipientEmail}
            onChange={(e) => {
              setRecipientEmail(e.target.value)
              if (error) {
                setError('')
              }
            }}
            placeholder="you@example.com"
            className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all"
          />
          <p className="mt-2 text-xs text-slate-500">
            We&apos;ll send a copy of the full report if provided.
          </p>
        </div>

        <button
          type="submit"
          className="mt-8 w-full px-6 py-4 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 transition-colors shadow-soft disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={isLocked}
        >
          Analyze Funnel
        </button>
      </form>

      <div className="mt-6 text-center text-sm text-slate-500">
        <p>Analysis typically takes 15-45 seconds</p>
      </div>
    </motion.div>
  )
}
