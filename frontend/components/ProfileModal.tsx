'use client'

import { useState } from 'react'
import { updateUserProfile } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'

interface ProfileModalProps {
  open: boolean
  onClose: () => void
  onProfileCompleted?: () => void
}

export function ProfileModal({ open, onClose, onProfileCompleted }: ProfileModalProps) {
  const [fullName, setFullName] = useState('')
  const [company, setCompany] = useState('')
  const [jobTitle, setJobTitle] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const token = useAuthStore((state) => state.token)

  if (!open) {
    return null
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMessage(null)

    if (!token) {
      setErrorMessage('Not authenticated. Please log in again.')
      return
    }

    setSubmitting(true)

    try {
      await updateUserProfile(token, {
        full_name: fullName || undefined,
        company: company || undefined,
        job_title: jobTitle || undefined,
        onboarding_completed: true,
      })
      
      setFullName('')
      setCompany('')
      setJobTitle('')
      onProfileCompleted?.()
      onClose()
    } catch (error: any) {
      setErrorMessage(error.message || 'Failed to update profile')
    } finally {
      setSubmitting(false)
    }
  }

  const handleSkip = () => {
    setFullName('')
    setCompany('')
    setJobTitle('')
    setErrorMessage(null)
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
      <div className="relative w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
        <button
          type="button"
          onClick={handleSkip}
          className="absolute right-4 top-4 rounded-lg p-1 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600"
          aria-label="Skip"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <div className="mb-6">
          <h2 className="text-2xl font-bold text-slate-900">Complete your profile</h2>
          <p className="mt-2 text-sm text-slate-600">
            Help us personalize your experience. You can skip this step and complete it later in settings.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="fullName" className="block text-sm font-medium text-slate-700">
              Full name
            </label>
            <input
              id="fullName"
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Taylor Johnson"
              className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-100"
              disabled={submitting}
            />
          </div>

          <div>
            <label htmlFor="company" className="block text-sm font-medium text-slate-700">
              Company
            </label>
            <input
              id="company"
              type="text"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              placeholder="Acme Inc."
              className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-100"
              disabled={submitting}
            />
          </div>

          <div>
            <label htmlFor="jobTitle" className="block text-sm font-medium text-slate-700">
              Job title
            </label>
            <input
              id="jobTitle"
              type="text"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              placeholder="Marketing Manager"
              className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-100"
              disabled={submitting}
            />
          </div>

          {errorMessage && (
            <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700" role="alert">
              {errorMessage}
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={handleSkip}
              disabled={submitting}
              className="flex-1 rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Skip for now
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="flex-1 rounded-xl bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-primary-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {submitting ? 'Saving...' : 'Save profile'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
