"use client";

import { useState, useEffect } from "react";
import { FiX, FiExternalLink } from "react-icons/fi";

interface UserAnalysis {
  id: number;
  overall_score: number;
  status: string;
  urls: string[];
  created_at: string;
  analysis_duration_seconds: number | null;
  error_message: string | null;
}

interface UserAnalysesModalProps {
  isOpen: boolean;
  onClose: () => void;
  userId: number;
  userEmail: string;
}

export default function UserAnalysesModal({ isOpen, onClose, userId, userEmail }: UserAnalysesModalProps) {
  const [analyses, setAnalyses] = useState<UserAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadAnalyses();
    }
  }, [isOpen, userId]);

  const loadAnalyses = async () => {
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem("token");
      if (!token) {
        throw new Error("Not authenticated");
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/admin/users/${userId}/analyses`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to load analyses");
      }

      const data = await response.json();
      setAnalyses(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto rounded-lg bg-white p-6 shadow-xl">
        {/* Header */}
        <div className="mb-4 flex items-center justify-between sticky top-0 bg-white pb-4 border-b">
          <div>
            <h2 className="text-xl font-semibold text-slate-900">User Analyses</h2>
            <p className="text-sm text-slate-500">{userEmail}</p>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
          >
            <FiX className="h-5 w-5" />
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">
            {error}
          </div>
        )}

        {/* Content */}
        {loading ? (
          <div className="py-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-slate-600">Loading analyses...</p>
          </div>
        ) : analyses.length === 0 ? (
          <div className="py-12 text-center text-slate-500">
            No analyses found for this user
          </div>
        ) : (
          <div className="space-y-4">
            {analyses.map((analysis) => (
              <div
                key={analysis.id}
                className="border border-slate-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-2xl font-bold text-slate-900">
                        {analysis.overall_score}
                        <span className="text-sm text-slate-500 font-normal">/100</span>
                      </span>
                      <span
                        className={`px-2 py-1 text-xs font-semibold rounded-full ${
                          analysis.status === "completed"
                            ? "bg-green-100 text-green-800"
                            : analysis.status === "failed"
                            ? "bg-red-100 text-red-800"
                            : "bg-yellow-100 text-yellow-800"
                        }`}
                      >
                        {analysis.status}
                      </span>
                    </div>

                    <div className="text-sm text-slate-600 space-y-1">
                      <div>
                        <span className="font-medium">Date:</span>{" "}
                        {new Date(analysis.created_at).toLocaleString()}
                      </div>
                      {analysis.analysis_duration_seconds && (
                        <div>
                          <span className="font-medium">Duration:</span>{" "}
                          {analysis.analysis_duration_seconds}s
                        </div>
                      )}
                      <div>
                        <span className="font-medium">URLs:</span>
                        <div className="ml-4 mt-1 space-y-1">
                          {analysis.urls.map((url, idx) => (
                            <div key={idx} className="flex items-center gap-2">
                              <FiExternalLink className="h-3 w-3 text-slate-400 flex-shrink-0" />
                              <a
                                href={url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-600 hover:text-blue-800 hover:underline truncate"
                              >
                                {url}
                              </a>
                            </div>
                          ))}
                        </div>
                      </div>
                      {analysis.error_message && (
                        <div className="mt-2 p-2 bg-red-50 rounded text-red-700 text-xs">
                          <span className="font-medium">Error:</span> {analysis.error_message}
                        </div>
                      )}
                    </div>
                  </div>
                  <a
                    href={`/results?id=${analysis.id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-4 px-3 py-1 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg"
                  >
                    View
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
