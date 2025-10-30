'use client'

import { useState, useEffect, useRef } from 'react'
import { renameAnalysis } from '@/lib/api'

interface EditableAnalysisNameProps {
  analysisId: number
  initialName?: string | null
  userId?: number
  onNameChange?: (newName: string) => void
}

export default function EditableAnalysisName({
  analysisId,
  initialName,
  userId,
  onNameChange,
}: EditableAnalysisNameProps) {
  const [name, setName] = useState(initialName || '')
  const [isEditing, setIsEditing] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus()
      inputRef.current.select()
    }
  }, [isEditing])

  const handleSave = async () => {
    if (!name.trim()) {
      setName(initialName || '')
      setIsEditing(false)
      return
    }

    if (name === initialName) {
      setIsEditing(false)
      return
    }

    setIsSaving(true)
    setError(null)

    try {
      await renameAnalysis(analysisId, name.trim(), userId)
      setIsEditing(false)
      onNameChange?.(name.trim())
    } catch (err: any) {
      setError(err.message || 'Failed to save name')
      setName(initialName || '')
    } finally {
      setIsSaving(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSave()
    } else if (e.key === 'Escape') {
      setName(initialName || '')
      setIsEditing(false)
    }
  }

  const displayName = name || `Analysis #${analysisId}`

  if (isEditing) {
    return (
      <div className="flex items-center gap-2">
        <input
          ref={inputRef}
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          onBlur={handleSave}
          onKeyDown={handleKeyDown}
          className="text-3xl font-bold text-slate-900 border-b-2 border-primary-500 bg-transparent outline-none px-1 max-w-2xl"
          placeholder="Enter analysis name..."
          disabled={isSaving}
          maxLength={255}
        />
        {isSaving && (
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600"></div>
        )}
      </div>
    )
  }

  return (
    <div className="group">
      <h1
        className="text-3xl font-bold text-slate-900 cursor-pointer hover:text-primary-600 transition-colors inline-flex items-center gap-2"
        onClick={() => setIsEditing(true)}
        title="Click to edit name"
      >
        {displayName}
        <svg
          className="w-5 h-5 opacity-0 group-hover:opacity-50 transition-opacity"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
          />
        </svg>
      </h1>
      {error && (
        <p className="text-sm text-red-600 mt-1">{error}</p>
      )}
    </div>
  )
}
