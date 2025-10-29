"use client";

import { useState, useEffect } from "react";
import { FiX } from "react-icons/fi";

interface UserEditModalProps {
  isOpen: boolean;
  onClose: () => void;
  user: {
    id: number;
    email: string;
    full_name: string | null;
    plan: string;
    status: string;
    role: string;
  };
  onSuccess: () => void;
}

export default function UserEditModal({ isOpen, onClose, user, onSuccess }: UserEditModalProps) {
  const [fullName, setFullName] = useState(user.full_name || "");
  const [plan, setPlan] = useState(user.plan);
  const [status, setStatus] = useState(user.status);
  const [role, setRole] = useState(user.role);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reset form when user changes
  useEffect(() => {
    setFullName(user.full_name || "");
    setPlan(user.plan);
    setStatus(user.status);
    setRole(user.role);
    setError(null);
  }, [user]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem("token");
      if (!token) {
        throw new Error("Not authenticated");
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/users/${user.id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          full_name: fullName || null,
          plan,
          status,
          role,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to update user");
      }

      onSuccess();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="relative w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
        {/* Header */}
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-slate-900">Edit User</h2>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
            disabled={loading}
          >
            <FiX className="h-5 w-5" />
          </button>
        </div>

        {/* User Info */}
        <div className="mb-4 rounded-lg bg-slate-50 p-3">
          <p className="text-sm font-medium text-slate-900">{user.email}</p>
          <p className="text-xs text-slate-500">User ID: {user.id}</p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit}>
          {/* Full Name */}
          <div className="mb-4">
            <label htmlFor="fullName" className="mb-1 block text-sm font-medium text-slate-700">
              Full Name
            </label>
            <input
              id="fullName"
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="Enter full name"
              disabled={loading}
            />
          </div>

          {/* Plan */}
          <div className="mb-4">
            <label htmlFor="plan" className="mb-1 block text-sm font-medium text-slate-700">
              Plan
            </label>
            <select
              id="plan"
              value={plan}
              onChange={(e) => setPlan(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              disabled={loading}
            >
              <option value="free">Free</option>
              <option value="basic">Basic</option>
              <option value="pro">Pro</option>
            </select>
          </div>

          {/* Status */}
          <div className="mb-4">
            <label htmlFor="status" className="mb-1 block text-sm font-medium text-slate-700">
              Status
            </label>
            <select
              id="status"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              disabled={loading}
            >
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="suspended">Suspended</option>
              <option value="canceled">Canceled</option>
              <option value="past_due">Past Due</option>
            </select>
          </div>

          {/* Role */}
          <div className="mb-6">
            <label htmlFor="role" className="mb-1 block text-sm font-medium text-slate-700">
              Role
            </label>
            <select
              id="role"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              disabled={loading}
            >
              <option value="member">Member</option>
              <option value="admin">Admin</option>
            </select>
            <p className="mt-1 text-xs text-slate-500">
              Be careful when changing roles - admins have full access
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? "Saving..." : "Save Changes"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
