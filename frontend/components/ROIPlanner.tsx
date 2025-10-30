'use client'

import { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { FiRefreshCw, FiTrendingUp, FiUsers, FiTarget, FiDollarSign } from 'react-icons/fi'

interface ROIPlannerProps {
  defaultVisitors?: number
  defaultConversionRate?: number
  defaultAverageOrderValue?: number
  defaultExpectedLift?: number
}

interface PlannerInputs {
  visitors: number
  conversionRate: number
  averageOrderValue: number
  expectedLift: number
}

const scenarioPresets = [
  { label: 'Conservative', expectedLift: 0.4 },
  { label: 'Likely', expectedLift: 0.8 },
  { label: 'Stretch', expectedLift: 1.2 },
]

const sanitizeNumber = (value: number) => {
  if (Number.isNaN(value) || !Number.isFinite(value)) {
    return 0
  }
  return Math.max(0, value)
}

export default function ROIPlanner({
  defaultVisitors = 12000,
  defaultConversionRate = 1.6,
  defaultAverageOrderValue = 138,
  defaultExpectedLift = 0.8,
}: ROIPlannerProps) {
  const [inputs, setInputs] = useState<PlannerInputs>({
    visitors: defaultVisitors,
    conversionRate: defaultConversionRate,
    averageOrderValue: defaultAverageOrderValue,
    expectedLift: defaultExpectedLift,
  })

  const metrics = useMemo(() => {
    const visitors = sanitizeNumber(inputs.visitors)
    const conversionRate = sanitizeNumber(inputs.conversionRate)
    const averageOrderValue = sanitizeNumber(inputs.averageOrderValue)
    const expectedLift = sanitizeNumber(inputs.expectedLift)

    const baselineConversionRate = conversionRate / 100
    const upliftConversionRate = (conversionRate + expectedLift) / 100

    const baselineCustomers = visitors * baselineConversionRate
    const improvedCustomers = visitors * upliftConversionRate
    const incrementalCustomers = Math.max(0, improvedCustomers - baselineCustomers)

    const baselineRevenue = baselineCustomers * averageOrderValue
    const projectedRevenue = improvedCustomers * averageOrderValue
    const monthlyLift = Math.max(0, projectedRevenue - baselineRevenue)
    const annualLift = monthlyLift * 12

    return {
      visitors,
      conversionRate,
      upliftConversionRate,
      averageOrderValue,
      expectedLift,
      baselineCustomers,
      improvedCustomers,
      incrementalCustomers,
      baselineRevenue,
      projectedRevenue,
      monthlyLift,
      annualLift,
    }
  }, [inputs])

  const updateInput = (key: keyof PlannerInputs, value: number) => {
    setInputs((prev) => ({
      ...prev,
      [key]: sanitizeNumber(value),
    }))
  }

  const resetInputs = () => {
    setInputs({
      visitors: defaultVisitors,
      conversionRate: defaultConversionRate,
      averageOrderValue: defaultAverageOrderValue,
      expectedLift: defaultExpectedLift,
    })
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white border border-slate-200 rounded-3xl shadow-lg/40 shadow-slate-500/10 p-6 xl:p-8"
    >
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold tracking-[0.2em] uppercase text-slate-500">ROI Planner</p>
          <h3 className="mt-2 text-xl font-bold text-slate-900">Customize your revenue assumptions</h3>
          <p className="mt-1 text-sm text-slate-500">
            Adjust these live inputs to see how funnel improvements translate into real revenue gains.
          </p>
        </div>
        <button
          onClick={resetInputs}
          className="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 shadow-sm transition hover:border-slate-300 hover:text-slate-900"
        >
          <FiRefreshCw className="h-3.5 w-3.5" /> Reset
        </button>
      </div>

      <div className="mt-6 grid gap-5 sm:grid-cols-2">
        <label className="flex flex-col">
          <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">Monthly Visitors</span>
          <div className="mt-2 flex items-center overflow-hidden rounded-xl border border-slate-200 bg-slate-50/60 focus-within:border-slate-400">
            <span className="px-3 text-sm font-semibold text-slate-500">👥</span>
            <input
              type="number"
              min={0}
              value={inputs.visitors}
              onChange={(event) => updateInput('visitors', Number(event.target.value))}
              className="flex-1 bg-transparent px-3 py-2 text-sm font-semibold text-slate-800 outline-none"
            />
          </div>
        </label>

        <label className="flex flex-col">
          <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">Current Conversion Rate (%)</span>
          <div className="mt-2 flex items-center overflow-hidden rounded-xl border border-slate-200 bg-slate-50/60 focus-within:border-slate-400">
            <span className="px-3 text-sm font-semibold text-slate-500">🎯</span>
            <input
              type="number"
              min={0}
              step={0.1}
              value={inputs.conversionRate}
              onChange={(event) => updateInput('conversionRate', Number(event.target.value))}
              className="flex-1 bg-transparent px-3 py-2 text-sm font-semibold text-slate-800 outline-none"
            />
          </div>
        </label>

        <label className="flex flex-col">
          <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">Average Order Value ($)</span>
          <div className="mt-2 flex items-center overflow-hidden rounded-xl border border-slate-200 bg-slate-50/60 focus-within:border-slate-400">
            <span className="px-3 text-sm font-semibold text-slate-500">💳</span>
            <input
              type="number"
              min={0}
              step={1}
              value={inputs.averageOrderValue}
              onChange={(event) => updateInput('averageOrderValue', Number(event.target.value))}
              className="flex-1 bg-transparent px-3 py-2 text-sm font-semibold text-slate-800 outline-none"
            />
          </div>
        </label>

        <label className="flex flex-col">
          <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">Expected Conversion Lift (points)</span>
          <div className="mt-2 flex items-center overflow-hidden rounded-xl border border-slate-200 bg-slate-50/60 focus-within:border-slate-400">
            <span className="px-3 text-sm font-semibold text-slate-500">⚡️</span>
            <input
              type="number"
              min={0}
              step={0.1}
              value={inputs.expectedLift}
              onChange={(event) => updateInput('expectedLift', Number(event.target.value))}
              className="flex-1 bg-transparent px-3 py-2 text-sm font-semibold text-slate-800 outline-none"
            />
          </div>
        </label>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2">
        <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">Scenarios</span>
        {scenarioPresets.map((scenario) => {
          const isActive = Number(inputs.expectedLift.toFixed(1)) === Number(scenario.expectedLift.toFixed(1))

          return (
            <button
              key={scenario.label}
              onClick={() => updateInput('expectedLift', scenario.expectedLift)}
              className={`rounded-full border px-3 py-1.5 text-xs font-semibold transition ${
                isActive
                  ? 'border-emerald-500 bg-emerald-500/10 text-emerald-700'
                  : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:text-slate-900'
              }`}
            >
              {scenario.label} · +{scenario.expectedLift}%
            </button>
          )
        })}
      </div>

      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        <div className="rounded-2xl bg-slate-900 text-slate-100 p-6">
          <div className="flex items-center justify-between text-xs uppercase tracking-wide text-slate-400">
            <span>Monthly Revenue Lift</span>
            <FiTrendingUp className="h-4 w-4" />
          </div>
          <div className="mt-3 text-3xl font-bold tracking-tight">
            ${Math.round(metrics.monthlyLift).toLocaleString()}
          </div>
          <p className="mt-2 text-sm text-slate-400">
            Current revenue {metrics.baselineRevenue > 0 ? `~$${Math.round(metrics.baselineRevenue).toLocaleString()}/mo` : 'not set'}
          </p>
        </div>
        <div className="rounded-2xl border border-emerald-200 bg-emerald-50/60 p-6">
          <div className="flex items-center justify-between text-xs uppercase tracking-wide text-emerald-600">
            <span>Annualized Impact</span>
            <FiDollarSign className="h-4 w-4" />
          </div>
          <div className="mt-3 text-3xl font-bold text-emerald-700">
            ${Math.round(metrics.annualLift).toLocaleString()}
          </div>
          <p className="mt-2 text-sm text-emerald-700/80">
            Assuming improvements hold steady for 12 months.
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-700">
            <FiUsers className="h-4 w-4" />
            Additional customers / month
          </div>
          <p className="mt-2 text-2xl font-bold text-slate-900">
            +{Math.round(metrics.incrementalCustomers).toLocaleString()}
          </p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-700">
            <FiTarget className="h-4 w-4" />
            Projected conversion rate
          </div>
          <p className="mt-2 text-2xl font-bold text-slate-900">
            {metrics.upliftConversionRate.toFixed(2)}%
          </p>
          <p className="text-xs text-slate-500">Up from {metrics.conversionRate.toFixed(2)}%</p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-700">
            <FiTrendingUp className="h-4 w-4" />
            Pipeline value (monthly)
          </div>
          <p className="mt-2 text-2xl font-bold text-slate-900">
            ${Math.round(metrics.projectedRevenue).toLocaleString()}
          </p>
          <p className="text-xs text-slate-500">
            From ${Math.round(metrics.baselineRevenue).toLocaleString()} baseline
          </p>
        </div>
      </div>
    </motion.div>
  )
}
