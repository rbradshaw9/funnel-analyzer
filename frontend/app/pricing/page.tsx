import Link from 'next/link'
import { TopNav } from '@/components/TopNav'
import {
  FUNNEL_ANALYZER_BASIC_CHECKOUT_URL,
  FUNNEL_ANALYZER_PRO_CHECKOUT_URL,
  FUNNEL_ANALYZER_JOIN_URL,
} from '@/lib/externalLinks'

const plans = [
  {
    name: 'Basic',
    price: '$59/mo',
    description: 'Solo operators tracking a handful of funnels each month.',
    checkoutUrl: FUNNEL_ANALYZER_BASIC_CHECKOUT_URL,
    highlight: false,
    features: [
      '1 workspace',
      'Up to 3 funnels tracked',
      '10 analyses per month',
      'Core AI scoring & breakdowns',
      'PDF and CSV exports',
      'Weekly performance digests',
      'Community office hours access',
    ],
  },
  {
    name: 'Pro',
    price: '$149/mo',
    description: 'Agencies and growth teams needing deep insights at scale.',
    checkoutUrl: FUNNEL_ANALYZER_PRO_CHECKOUT_URL,
    highlight: true,
    features: [
      'Unlimited workspaces & funnels',
      'Unlimited analyses',
      'Up to 5 team seats',
      'Screenshot diffing + change alerts',
      'CRM & Zapier integrations',
      'API + custom branding on reports',
      'Priority chat and quarterly expert audit',
    ],
  },
]

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      <TopNav
        rightSlot={
          <div className="flex items-center gap-4">
            <Link href="/free-analysis" className="text-sm font-medium text-slate-600 hover:text-slate-900">
              Free Analysis
            </Link>
            <Link
              href={FUNNEL_ANALYZER_JOIN_URL}
              className="inline-flex items-center px-5 py-2 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-sm font-semibold shadow-md hover:from-indigo-700 hover:to-purple-700 transition-colors"
            >
              Start Now
            </Link>
          </div>
        }
      />

      <main className="mx-auto flex max-w-6xl flex-col gap-16 px-4 py-16 sm:px-6 lg:px-8">
        <section className="text-center">
          <p className="text-sm font-semibold uppercase tracking-wide text-indigo-600">Pricing</p>
          <h1 className="mt-2 text-4xl font-extrabold text-slate-900 sm:text-5xl">Choose the plan that fits your funnels</h1>
          <p className="mx-auto mt-4 max-w-3xl text-lg text-slate-600">
            Start free, pick a plan when you&apos;re ready. Every subscription includes battle-tested AI analysis,
            unlimited saved reports, and secure sharing with clients or teammates.
          </p>
        </section>

        <section className="grid gap-8 md:grid-cols-2">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`flex flex-col rounded-3xl border bg-white p-8 shadow-xl transition hover:shadow-2xl ${
                plan.highlight
                  ? 'border-indigo-300 ring-4 ring-indigo-200'
                  : 'border-slate-200'
              }`}
            >
              <div className="flex items-baseline justify-between">
                <h2 className="text-2xl font-bold text-slate-900">{plan.name}</h2>
                {plan.highlight && (
                  <span className="rounded-full bg-indigo-600 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-white">
                    Most Popular
                  </span>
                )}
              </div>
              <p className="mt-3 text-sm text-slate-500">{plan.description}</p>
              <p className="mt-6 text-4xl font-extrabold text-slate-900">{plan.price}</p>

              <Link
                href={plan.checkoutUrl}
                className={`mt-8 inline-flex w-full items-center justify-center rounded-xl px-6 py-3 text-sm font-semibold shadow-lg transition ${
                  plan.highlight
                    ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700'
                    : 'bg-slate-900 text-white hover:bg-slate-800'
                }`}
              >
                {plan.name === 'Basic' ? 'Start Basic' : 'Upgrade to Pro'}
              </Link>

              <ul className="mt-8 space-y-3 text-sm text-slate-600">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-3">
                    <span className="mt-0.5 inline-flex h-2.5 w-2.5 rounded-full bg-indigo-500" aria-hidden="true" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </section>

        <section className="rounded-3xl bg-white p-10 shadow-lg border border-slate-200">
          <div className="grid gap-8 md:grid-cols-2 md:items-center">
            <div>
              <h2 className="text-2xl font-bold text-slate-900">Need a custom setup?</h2>
              <p className="mt-3 text-sm text-slate-600">
                Enterprise compliance, white-labeled deliverables, or large team rollouts are available. Let&apos;s design a
                plan that fits your pipeline and throughput goals.
              </p>
            </div>
            <div className="flex flex-col gap-4">
              <Link
                href="mailto:sales@funnelanalyzerpro.com"
                className="inline-flex items-center justify-center rounded-xl border border-slate-200 px-6 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-indigo-200 hover:text-indigo-700"
              >
                Talk with sales
              </Link>
              <Link
                href="/free-analysis"
                className="inline-flex items-center justify-center rounded-xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white shadow-md transition hover:bg-slate-800"
              >
                Keep exploring the demo
              </Link>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}
