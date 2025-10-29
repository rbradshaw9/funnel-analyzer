"use client"

import { useState } from 'react'
import { AuthModal } from './AuthModal'

interface LoginButtonProps {
  className?: string
}

export function LoginButton({ className }: LoginButtonProps) {
  const [open, setOpen] = useState(false)

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className={[
          'text-sm font-semibold text-primary-600 hover:text-primary-700 transition-colors',
          className ?? '',
        ].filter(Boolean).join(' ')}
      >
        Log in
      </button>

      <AuthModal 
        open={open} 
        onClose={() => setOpen(false)} 
        defaultMode="login"
      />
    </>
  )
}
