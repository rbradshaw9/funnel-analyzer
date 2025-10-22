import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Funnel Analyzer Pro - AI-Powered Funnel Analysis',
  description: 'Analyze your marketing funnels with AI to optimize conversions',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
