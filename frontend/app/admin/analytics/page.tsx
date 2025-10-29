"use client"

import AdminLayout from "@/components/AdminLayout"
import { FiBarChart2 } from "react-icons/fi"

export default function AnalyticsPage() {
  return (
    <AdminLayout>
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-xl shadow-sm p-12 text-center">
          <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-6">
            <FiBarChart2 className="w-10 h-10 text-white" />
          </div>
          
          <h1 className="text-3xl font-bold text-slate-900 mb-4">Analytics Dashboard</h1>
          <p className="text-slate-600 mb-8">
            Platform analytics and insights coming soon. This page will display user engagement metrics, 
            funnel analysis trends, and other key performance indicators.
          </p>
          
          <div className="inline-flex items-center text-sm text-blue-600 font-medium">
            <span className="w-2 h-2 bg-blue-600 rounded-full mr-2 animate-pulse"></span>
            Under Development
          </div>
        </div>
      </div>
    </AdminLayout>
  )
}
