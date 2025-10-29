"use client"

import { useEffect, useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { FiChevronDown, FiChevronUp } from "react-icons/fi"
import { useAuthStore } from "@/store/authStore"
import { AuthModal } from "@/components/AuthModal"
import AdminLayout from "@/components/AdminLayout"
import UserEditModal from "@/components/UserEditModal"
import UserAnalysesModal from "@/components/UserAnalysesModal"

interface UserStats {
  total_users: number
  active_users: number
  free_users: number
  basic_users: number
  pro_users: number
  total_analyses: number
  analyses_today: number
}

interface UserListItem {
  id: number
  email: string
  full_name: string | null
  plan: string
  status: string
  role: string
  created_at: string
  analysis_count: number
  oauth_provider: string | null
}

interface UserDetail extends UserListItem {
  subscription_id: string | null
  thrivecart_customer_id: string | null
  access_expires_at: string | null
  status_reason: string | null
  updated_at: string | null
}

export default function AdminPage() {
  const router = useRouter()
  const { token } = useAuthStore()
  const [stats, setStats] = useState<UserStats | null>(null)
  const [users, setUsers] = useState<UserListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [filterPlan, setFilterPlan] = useState<string>("")
  const [filterStatus, setFilterStatus] = useState<string>("")
  const [searchTerm, setSearchTerm] = useState("")
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [editingUser, setEditingUser] = useState<UserListItem | null>(null)
  const [expandedUserId, setExpandedUserId] = useState<number | null>(null)
  const [userDetails, setUserDetails] = useState<Map<number, UserDetail>>(new Map())
  const [viewingAnalysesUserId, setViewingAnalysesUserId] = useState<number | null>(null)
  const [viewingAnalysesUserEmail, setViewingAnalysesUserEmail] = useState<string>("")

  const loadData = useCallback(async () => {
    try {
      setLoading(true)
      
      // Load stats
      const statsRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      if (!statsRes.ok) {
        if (statsRes.status === 403) {
          setError("Admin access required")
          return
        }
        throw new Error("Failed to load stats")
      }
      
      const statsData = await statsRes.json()
      setStats(statsData)
      
      // Load users
      const params = new URLSearchParams()
      if (filterPlan) params.append("plan", filterPlan)
      if (filterStatus) params.append("status", filterStatus)
      if (searchTerm) params.append("search", searchTerm)
      
      const usersRes = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/admin/users?${params}`,
        { headers: { Authorization: `Bearer ${token}` } }
      )
      
      if (!usersRes.ok) throw new Error("Failed to load users")
      
      const usersData = await usersRes.json()
      setUsers(usersData)
      
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [token, filterPlan, filterStatus, searchTerm])

  useEffect(() => {
    if (token) {
      loadData()
    } else {
      setLoading(false)
    }
  }, [token, filterPlan, filterStatus, searchTerm, loadData])

  const deleteUser = async (userId: number, email: string) => {
    if (!confirm(`Are you sure you want to delete user ${email}? This cannot be undone.`)) {
      return
    }

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/users/${userId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      })

      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || "Failed to delete user")
      }

      // Reload data
      await loadData()
      alert(`User ${email} deleted successfully`)
    } catch (err: any) {
      alert(`Error: ${err.message}`)
    }
  }

  const toggleUserExpand = async (userId: number) => {
    if (expandedUserId === userId) {
      setExpandedUserId(null)
      return
    }

    setExpandedUserId(userId)

    // Load user details if not already loaded
    if (!userDetails.has(userId)) {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/users/${userId}`, {
          headers: { Authorization: `Bearer ${token}` }
        })

        if (!res.ok) throw new Error("Failed to load user details")

        const detail: UserDetail = await res.json()
        setUserDetails(new Map(userDetails.set(userId, detail)))
      } catch (err) {
        console.error("Error loading user details:", err)
      }
    }
  }

  if (error === "Admin access required") {
    return (
      <AdminLayout>
        <div className="max-w-2xl mx-auto text-center">
          <h1 className="text-3xl font-bold text-slate-900 mb-4">Access Denied</h1>
          <p className="text-slate-600">You need admin privileges to access this page.</p>
        </div>
      </AdminLayout>
    )
  }

  // Not logged in - show login prompt
  if (!token) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="container mx-auto px-4 py-20">
          <div className="max-w-2xl mx-auto text-center">
            <div className="bg-white rounded-2xl shadow-lg p-12">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              
              <h1 className="text-3xl font-bold text-slate-900 mb-4">Admin Login Required</h1>
              <p className="text-slate-600 mb-8">Please sign in with your admin account to access the admin dashboard.</p>
              
              <button
                onClick={() => setShowAuthModal(true)}
                className="inline-flex items-center px-8 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg hover:shadow-xl"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                </svg>
                Sign In
              </button>
              
              <p className="text-sm text-slate-500 mt-6">
                Admin access is restricted to authorized personnel only.
              </p>
            </div>
          </div>
        </div>
        
        <AuthModal 
          open={showAuthModal} 
          onClose={() => setShowAuthModal(false)} 
          defaultMode="login"
        />
      </div>
    )
  }

  return (
    <AdminLayout>
      <div className="container mx-auto">
        <h1 className="text-4xl font-bold text-slate-900 mb-8">Admin Dashboard</h1>

        {error && error !== "Admin access required" && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
            {error}
          </div>
        )}

        {/* Stats Grid */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            <StatCard label="Total Users" value={stats.total_users} />
            <StatCard label="Active Users" value={stats.active_users} />
            <StatCard label="Total Analyses" value={stats.total_analyses} />
            <StatCard label="Analyses Today" value={stats.analyses_today} />
            <StatCard label="Free Plan" value={stats.free_users} color="slate" />
            <StatCard label="Basic Plan" value={stats.basic_users} color="blue" />
            <StatCard label="Pro Plan" value={stats.pro_users} color="purple" />
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
          <h2 className="text-xl font-semibold text-slate-900 mb-4">User Management</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Search</label>
              <input
                type="text"
                placeholder="Email or name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Plan</label>
              <select
                value={filterPlan}
                onChange={(e) => setFilterPlan(e.target.value)}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Plans</option>
                <option value="free">Free</option>
                <option value="basic">Basic</option>
                <option value="pro">Pro</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Status</label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Statuses</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="suspended">Suspended</option>
                <option value="canceled">Canceled</option>
              </select>
            </div>
          </div>
        </div>

        {/* Users Table */}
        {loading ? (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-slate-600">Loading...</p>
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider w-8"></th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">User</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Plan</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Role</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Analyses</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Created</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-slate-200">
                  {users.map((user) => {
                    const isExpanded = expandedUserId === user.id
                    const detail = userDetails.get(user.id)
                    
                    return (
                      <>
                        <tr key={user.id} className="hover:bg-slate-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <button
                              onClick={() => toggleUserExpand(user.id)}
                              className="text-slate-400 hover:text-slate-600"
                            >
                              {isExpanded ? <FiChevronUp className="h-4 w-4" /> : <FiChevronDown className="h-4 w-4" />}
                            </button>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div>
                                <div className="text-sm font-medium text-slate-900">{user.email}</div>
                                {user.full_name && (
                                  <div className="text-sm text-slate-500">{user.full_name}</div>
                                )}
                                {user.oauth_provider && (
                                  <div className="text-xs text-slate-400">OAuth: {user.oauth_provider}</div>
                                )}
                              </div>
                            </div>
                          </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          user.plan === 'pro' ? 'bg-purple-100 text-purple-800' :
                          user.plan === 'basic' ? 'bg-blue-100 text-blue-800' :
                          'bg-slate-100 text-slate-800'
                        }`}>
                          {user.plan}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          user.status === 'active' ? 'bg-green-100 text-green-800' :
                          user.status === 'suspended' ? 'bg-red-100 text-red-800' :
                          'bg-slate-100 text-slate-800'
                        }`}>
                          {user.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                        {user.role}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                        {user.analysis_count}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                        {new Date(user.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex gap-2">
                          <button
                            onClick={() => {
                              setViewingAnalysesUserId(user.id)
                              setViewingAnalysesUserEmail(user.email)
                            }}
                            className="text-purple-600 hover:text-purple-900"
                          >
                            Analyses
                          </button>
                          <button
                            onClick={() => setEditingUser(user)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            Edit
                          </button>
                          {user.role !== 'admin' && (
                            <button
                              onClick={() => deleteUser(user.id, user.email)}
                              className="text-red-600 hover:text-red-900"
                            >
                              Delete
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                    
                    {/* Expanded Detail Row */}
                    {isExpanded && detail && (
                      <tr key={`${user.id}-detail`} className="bg-slate-50">
                        <td colSpan={8} className="px-6 py-4">
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <h4 className="font-semibold text-slate-700 mb-2">Subscription Details</h4>
                              <div className="space-y-1 text-slate-600">
                                <div><span className="font-medium">Subscription ID:</span> {detail.subscription_id || "N/A"}</div>
                                <div><span className="font-medium">ThriveCart Customer ID:</span> {detail.thrivecart_customer_id || "N/A"}</div>
                                <div><span className="font-medium">Access Expires:</span> {detail.access_expires_at ? new Date(detail.access_expires_at).toLocaleString() : "Never"}</div>
                                <div><span className="font-medium">Status Reason:</span> {detail.status_reason || "N/A"}</div>
                              </div>
                            </div>
                            <div>
                              <h4 className="font-semibold text-slate-700 mb-2">Account Information</h4>
                              <div className="space-y-1 text-slate-600">
                                <div><span className="font-medium">User ID:</span> {detail.id}</div>
                                <div><span className="font-medium">Created:</span> {new Date(detail.created_at).toLocaleString()}</div>
                                <div><span className="font-medium">Last Updated:</span> {detail.updated_at ? new Date(detail.updated_at).toLocaleString() : "N/A"}</div>
                                <div><span className="font-medium">Total Analyses:</span> {detail.analysis_count}</div>
                              </div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </>
                    )
                  })}
                </tbody>
              </table>
            </div>
            
            {users.length === 0 && (
              <div className="text-center py-12 text-slate-500">
                No users found
              </div>
            )}
          </div>
        )}
      </div>

      {/* Edit User Modal */}
      {editingUser && (
        <UserEditModal
          isOpen={!!editingUser}
          onClose={() => setEditingUser(null)}
          user={editingUser}
          onSuccess={() => {
            setEditingUser(null)
            loadData()
          }}
        />
      )}

      {/* User Analyses Modal */}
      {viewingAnalysesUserId && (
        <UserAnalysesModal
          isOpen={!!viewingAnalysesUserId}
          onClose={() => {
            setViewingAnalysesUserId(null)
            setViewingAnalysesUserEmail("")
          }}
          userId={viewingAnalysesUserId}
          userEmail={viewingAnalysesUserEmail}
        />
      )}
    </AdminLayout>
  )
}

function StatCard({ label, value, color = "blue" }: { label: string; value: number; color?: string }) {
  const colorClasses = {
    blue: "from-blue-500 to-blue-600",
    purple: "from-purple-500 to-purple-600",
    slate: "from-slate-500 to-slate-600",
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl shadow-sm p-6"
    >
      <div className={`inline-flex p-3 rounded-lg bg-gradient-to-br ${colorClasses[color as keyof typeof colorClasses]} mb-4`}>
        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      </div>
      <h3 className="text-sm font-medium text-slate-600">{label}</h3>
      <p className="text-3xl font-bold text-slate-900 mt-2">{value.toLocaleString()}</p>
    </motion.div>
  )
}
