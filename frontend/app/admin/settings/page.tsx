"use client"

import AdminLayout from "@/components/AdminLayout"
import { FiSettings } from "react-icons/fi"

export default function SettingsPage() {
  return (
    <AdminLayout>
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-xl shadow-sm p-12 text-center">
          <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
            <FiSettings className="w-10 h-10 text-white" />
          </div>
          
          <h1 className="text-3xl font-bold text-slate-900 mb-4">Admin Settings</h1>
          <p className="text-slate-600 mb-8">
            Configure platform settings, manage integrations, and customize system behavior. 
            This page will include site configuration, API settings, and other administrative options.
          </p>
          
          <div className="inline-flex items-center text-sm text-purple-600 font-medium">
            <span className="w-2 h-2 bg-purple-600 rounded-full mr-2 animate-pulse"></span>
            Under Development
          </div>
        </div>
      </div>
    </AdminLayout>
  )
}
