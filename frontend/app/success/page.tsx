"use client"

import { Suspense } from 'react'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'

import { TopNav } from '@/components/TopNav'

type PlanKey = 'basic' | 'pro'

const PLAN_LIBRARY: Record<PlanKey, {
  label: string
  highlight: string
  benefits: string[]
}> = {
  basic: {
    label: 'Conversion Essentials Plan',
    highlight: 'You now have unlimited funnel analyses for one workspace plus stored reports for every project.',
    benefits: [
      'Unlimited AI funnel analyses for a single brand or client',
      'Full score breakdowns, page-by-page feedback, and screenshot storage',
      'Email delivery of every report for easy sharing',
      'Access to the member dashboard with saved history and re-run actions',
    ],
  },
  pro: {
    label: 'Growth Pro Plan',
    highlight: 'Your account now supports multiple workspaces, premium scoring, and white-labeled reports.',
    benefits: [
      'Unlimited analyses across multiple brands and funnels',
      'Advanced scoring that compares offer stack vs. price positioning',
      'Priority processing with expanded screenshot retention',
      'Team dashboard access plus ready-to-share PDF exports',
    ],
  },
}

const DEFAULT_PLAN = {
  label: 'Funnel Analyzer Membership',
  highlight: 'Your membership is active and your workspace has been upgraded.',
  benefits: [
    'Unlimited AI analyses while your membership remains active',
    'Detailed scorecards with clarity, value, proof, design, and flow insights',
    'Instant email delivery of every report to your inbox',
    'Member dashboard access for reruns, history, and asset downloads',
  ],
}

const SUPPORT_EMAIL = 'support@funnelanalyzerpro.com'

function PurchaseSuccessContent() {
  const searchParams = useSearchParams()
  const planParam = (searchParams.get('plan') || '').toLowerCase()
  const plan = isPlanKey(planParam) ? PLAN_LIBRARY[planParam] : DEFAULT_PLAN

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-accent-50">
      <TopNav />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <section className="text-center">
          <div className="inline-flex items-center gap-2 rounded-full bg-emerald-100 px-4 py-1.5 text-sm font-semibold text-emerald-700">
            <span role="img" aria-label="Celebration">🎉</span>
            Purchase confirmed
          </div>
          <h1 className="mt-6 text-4xl font-extrabold text-slate-900 sm:text-5xl">
            Welcome to {plan.label}
          </h1>
          <p className="mt-4 text-lg text-slate-600">
            {plan.highlight}
          </p>
          <p className="mt-2 text-base text-slate-500">
            We just sent a receipt and magic-link access email to the address you used at checkout.
            Look for it in the next couple of minutes.
          </p>

          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link
              href="/dashboard"
              className="inline-flex items-center justify-center rounded-xl bg-gradient-to-r from-primary-600 to-accent-500 px-6 py-3 text-sm font-semibold text-white shadow-lg transition hover:from-primary-700 hover:to-accent-600"
            >
              Go to the dashboard
            </Link>
            <a
              href={`mailto:${SUPPORT_EMAIL}`}
              className="inline-flex items-center justify-center rounded-xl border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50"
            >
              Email support
            </a>
          </div>
        </section>

        <section className="mt-16 grid gap-6 md:grid-cols-2">
          <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-soft">
            <h2 className="text-xl font-semibold text-slate-900">What happens next</h2>
                        <ol className="mt-4 space-y-4 text-left text-sm text-slate-600">
              <li className="flex items-start gap-3">
                <span className="mt-0.5 inline-flex h-7 w-7 items-center justify-center rounded-full bg-accent-600 text-sm font-semibold text-white">1</span>
                <div>
                  <p className="font-semibold text-slate-800">Open the magic-link email</p>
                  <p className="mt-1 text-slate-600">Click the secure sign-in link to activate your workspace and set a password if prompted.</p>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <span className="mt-0.5 inline-flex h-7 w-7 items-center justify-center rounded-full bg-accent-600 text-sm font-semibold text-white">2</span>
                <div>
                  <p className="font-semibold text-slate-800">Visit the dashboard</p>
                  <p className="mt-1 text-slate-600">Upload your first funnel or import a previous free analysis to unlock the full report builder.</p>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <span className="mt-0.5 inline-flex h-7 w-7 items-center justify-center rounded-full bg-accent-600 text-sm font-semibold text-white">3</span>
                <div>
                  <p className="font-semibold text-slate-800">Invite collaborators (optional)</p>
                  <p className="mt-1 text-slate-600">Forward the access email to teammates or add them from the dashboard settings panel.</p>
                </div>
              </li>
            </ol>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-soft">
            <h2 className="text-xl font-semibold text-slate-900">Your membership includes</h2>
            <ul className="mt-4 space-y-3 text-left text-sm text-slate-600">
              {plan.benefits.map((benefit) => (
                <li key={benefit} className="flex items-start gap-3">
                  <span className="mt-0.5 inline-flex h-6 w-6 items-center justify-center rounded-full bg-emerald-100 text-sm font-semibold text-emerald-600">✓</span>
                  <span>{benefit}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section className="mt-16">
          <div className="rounded-3xl border border-accent-200 bg-accent-50 px-6 py-8 sm:px-10">
            <h3 className="text-lg font-semibold text-accent-900">Need anything else?</h3>
            <p className="mt-2 text-sm text-accent-800">
              If you have trouble accessing your account, need to upgrade/downgrade, or want to add an upsell after checkout,
              reply to the onboarding email or reach us directly at <a href={`mailto:${SUPPORT_EMAIL}`} className="font-semibold text-accent-900 underline">{SUPPORT_EMAIL}</a>.
              Our team typically responds within one business day.
            </p>
          </div>
        </section>
      </main>
    </div>
  )
}

function LoadingState() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-accent-50">
      <TopNav />
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <section className="text-center">
          <div className="inline-flex items-center gap-2 rounded-full bg-primary-100 px-4 py-1.5 text-sm font-semibold text-primary-600">
            Preparing your account...
          </div>
        </section>
      </main>
    </div>
  )
}

export default function PurchaseSuccessPage() {
  return (
    <Suspense fallback={<LoadingState />}>
      <PurchaseSuccessContent />
    </Suspense>
  )
}

function isPlanKey(value: string): value is PlanKey {
  return value === 'basic' || value === 'pro'
}
