'use client'

import { Radar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  ChartOptions,
} from 'chart.js'

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
)

interface ScoreChartProps {
  currentScores: {
    clarity: number
    value: number
    proof: number
    design: number
    flow: number
  }
  previousScores?: {
    clarity: number
    value: number
    proof: number
    design: number
    flow: number
  } | null
}

export default function ScoreComparisonChart({ currentScores, previousScores }: ScoreChartProps) {
  const labels = ['Clarity', 'Value', 'Proof', 'Design', 'Flow']
  
  const currentData = [
    currentScores.clarity,
    currentScores.value,
    currentScores.proof,
    currentScores.design,
    currentScores.flow,
  ]

  const previousData = previousScores ? [
    previousScores.clarity,
    previousScores.value,
    previousScores.proof,
    previousScores.design,
    previousScores.flow,
  ] : null

  const data = {
    labels,
    datasets: [
      ...(previousData ? [{
        label: 'Previous Report',
        data: previousData,
        backgroundColor: 'rgba(148, 163, 184, 0.1)',
        borderColor: 'rgba(148, 163, 184, 0.3)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(148, 163, 184, 0.5)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(148, 163, 184, 1)',
      }] : []),
      {
        label: 'Current Report',
        data: currentData,
        backgroundColor: 'rgba(16, 185, 129, 0.2)',
        borderColor: 'rgb(16, 185, 129)',
        borderWidth: 3,
        pointBackgroundColor: 'rgb(16, 185, 129)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgb(16, 185, 129)',
        pointRadius: 5,
        pointHoverRadius: 7,
      },
    ],
  }

  const options: ChartOptions<'radar'> = {
    responsive: true,
    maintainAspectRatio: true,
    scales: {
      r: {
        beginAtZero: true,
        max: 100,
        ticks: {
          stepSize: 20,
          font: {
            size: 11,
          },
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
        angleLines: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
        pointLabels: {
          font: {
            size: 13,
            weight: 'bold',
          },
          color: '#334155',
        },
      },
    },
    plugins: {
      legend: {
        display: !!previousData,
        position: 'bottom',
        labels: {
          padding: 15,
          font: {
            size: 12,
          },
          usePointStyle: true,
        },
      },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        padding: 12,
        titleFont: {
          size: 14,
          weight: 'bold',
        },
        bodyFont: {
          size: 13,
        },
        cornerRadius: 8,
        callbacks: {
          label: function(context) {
            const label = context.dataset.label || ''
            const value = context.parsed.r
            const delta = previousData && context.datasetIndex === 1 
              ? value - previousData[context.dataIndex]
              : null
            
            if (delta !== null) {
              const sign = delta >= 0 ? '+' : ''
              return `${label}: ${value} (${sign}${delta.toFixed(0)})`
            }
            return `${label}: ${value}`
          },
        },
      },
    },
  }

  return (
    <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
      <div className="mb-4">
        <h3 className="text-lg font-bold text-slate-900">Score Overview</h3>
        <p className="text-sm text-slate-600">
          {previousData ? 'Comparison with previous report' : 'Current performance across all dimensions'}
        </p>
      </div>
      <div className="relative" style={{ height: '300px' }}>
        <Radar data={data} options={options} />
      </div>
    </div>
  )
}
