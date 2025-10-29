'use client'

import { useRouter } from 'next/navigation'
import { useState, useRef, useEffect } from 'react'
import { useAuthStore } from '@/store/authStore'

interface UserMenuProps {
  userName?: string
  userEmail?: string
}

export function UserMenu({ userName, userEmail }: UserMenuProps) {
  const [isOpen, setIsOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)
  const router = useRouter()
  const reset = useAuthStore((state) => state.reset)

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const handleSignOut = () => {
    reset()
    setIsOpen(false)
    router.push('/')
  }

  const initials = userName
    ? userName
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    : userEmail
      ? userEmail[0].toUpperCase()
      : 'U'

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 p-0.5 transition-all hover:shadow-md"
        aria-label="User menu"
      >
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white text-sm font-semibold text-primary-600">
          {initials}
        </div>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 origin-top-right rounded-xl border border-slate-200 bg-white shadow-lg ring-1 ring-black ring-opacity-5">
          <div className="border-b border-slate-100 px-4 py-3">
            {userName && (
              <p className="text-sm font-semibold text-slate-900">{userName}</p>
            )}
            {userEmail && (
              <p className="text-xs text-slate-500 truncate">{userEmail}</p>
            )}
          </div>

          <div className="py-1">
            <button
              onClick={() => {
                setIsOpen(false)
                router.push('/dashboard')
              }}
              className="block w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-50"
            >
              Dashboard
            </button>
            <button
              onClick={() => {
                setIsOpen(false)
                router.push('/free-analysis')
              }}
              className="block w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-50"
            >
              Free Analysis
            </button>
          </div>

          <div className="border-t border-slate-100 py-1">
            <button
              onClick={handleSignOut}
              className="block w-full px-4 py-2 text-left text-sm text-rose-600 hover:bg-rose-50"
            >
              Sign out
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
