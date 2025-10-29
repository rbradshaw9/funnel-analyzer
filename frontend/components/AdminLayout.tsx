"use client"

import { usePathname, useRouter } from "next/navigation"
import { FiUsers, FiMail, FiBarChart2, FiSettings, FiLogOut } from "react-icons/fi"
import { TopNav } from "./TopNav"
import { useAuthStore } from "@/store/authStore"

interface AdminLayoutProps {
  children: React.ReactNode
}

const navItems = [
  { href: "/admin", icon: FiUsers, label: "Users" },
  { href: "/admin/emails", icon: FiMail, label: "Email Templates" },
  { href: "/admin/analytics", icon: FiBarChart2, label: "Analytics" },
  { href: "/admin/settings", icon: FiSettings, label: "Settings" },
]

export default function AdminLayout({ children }: AdminLayoutProps) {
  const pathname = usePathname()
  const router = useRouter()
  const reset = useAuthStore((state) => state.reset)

  const handleLogout = () => {
    reset()
    router.push("/")
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <TopNav showLoginButton={false} />
      
      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 min-h-[calc(100vh-4rem)] bg-white border-r border-slate-200 sticky top-16">
          <div className="p-6">
            <div className="mb-6">
              <h2 className="text-lg font-bold text-slate-900">Admin Panel</h2>
              <p className="text-xs text-slate-500 mt-1">Manage your platform</p>
            </div>

            <nav className="space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = pathname === item.href || 
                  (item.href !== "/admin" && pathname?.startsWith(item.href))
                
                return (
                  <button
                    key={item.href}
                    onClick={() => router.push(item.href)}
                    className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive
                        ? "bg-blue-50 text-blue-700"
                        : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                    {item.label}
                  </button>
                )
              })}
            </nav>

            <div className="mt-8 pt-8 border-t border-slate-200">
              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
              >
                <FiLogOut className="h-5 w-5" />
                Logout
              </button>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-8">
          {children}
        </main>
      </div>
    </div>
  )
}
