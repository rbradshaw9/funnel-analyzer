'use client'

import { FcGoogle } from 'react-icons/fc'
import { FaGithub } from 'react-icons/fa'

type OAuthProvider = 'google' | 'github'

interface OAuthButtonProps {
  provider: OAuthProvider
  onClick: () => void
  disabled?: boolean
}

const providerConfig = {
  google: {
    icon: FcGoogle,
    label: 'Continue with Google',
    bgColor: 'bg-white hover:bg-gray-50',
    textColor: 'text-gray-700',
    borderColor: 'border-gray-300',
  },
  github: {
    icon: FaGithub,
    label: 'Continue with GitHub',
    bgColor: 'bg-gray-900 hover:bg-gray-800',
    textColor: 'text-white',
    borderColor: 'border-gray-900',
  },
}

export function OAuthButton({ provider, onClick, disabled = false }: OAuthButtonProps) {
  const config = providerConfig[provider]
  const Icon = config.icon

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`
        flex w-full items-center justify-center gap-3 rounded-xl border px-4 py-2.5 text-sm font-semibold
        shadow-sm transition-all duration-200
        ${config.bgColor} ${config.textColor} ${config.borderColor}
        disabled:cursor-not-allowed disabled:opacity-50
        focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
      `}
    >
      <Icon className="h-5 w-5" />
      <span>{config.label}</span>
    </button>
  )
}
