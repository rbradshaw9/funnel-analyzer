'use client'

import type { ReactNode } from 'react'
import { useEffect, useState } from 'react'

import { LoginButton } from './LoginButton'
import { Logo } from './Logo'
import { UserMenu } from './UserMenu'
import { useAuthStore } from '@/store/authStore'

interface TopNavProps {
  rightSlot?: ReactNode
  translucent?: boolean
  sticky?: boolean
  className?: string
  showLoginButton?: boolean
}

export function TopNav({ rightSlot, translucent = true, sticky = true, className, showLoginButton = true }: TopNavProps) {
  const token = useAuthStore((state) => state.token)
  const [userEmail, setUserEmail] = useState<string | undefined>(undefined)
  
  // Decode email from JWT token
  useEffect(() => {
    if (!token) {
      setUserEmail(undefined)
      return
    }
    
    try {
      // JWT format: header.payload.signature
      const payload = token.split('.')[1]
      if (payload) {
        const decoded = JSON.parse(atob(payload))
        setUserEmail(decoded.email)
      }
    } catch (error) {
      console.warn('Failed to decode token', error)
      setUserEmail(undefined)
    }
  }, [token])
  
  const headerClasses = [
    'border-b border-primary-100/60',
    translucent ? 'bg-white/85 backdrop-blur-md' : 'bg-white',
    sticky ? 'sticky top-0 z-40' : '',
    className ?? '',
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <header className={headerClasses}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <Logo />
          <div className="flex items-center gap-4">
            {rightSlot}
            {token ? (
              <UserMenu userEmail={userEmail} />
            ) : showLoginButton ? (
              <LoginButton />
            ) : null}
          </div>
        </div>
      </div>
    </header>
  )
}
