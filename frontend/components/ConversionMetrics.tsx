/**
 * ConversionMetrics Component
 * 
 * Displays conversion statistics and attribution breakdown for a funnel analysis.
 */

'use client';

import React, { useEffect, useState } from 'react';
import { FiDollarSign, FiTrendingUp, FiUsers, FiTarget, FiAlertCircle } from 'react-icons/fi';

interface ConversionStats {
  total_conversions: number;
  attributed_conversions: number;
  attribution_rate: number;
  total_revenue: number;
  attribution_methods: Record<string, number>;
  avg_confidence?: number;
  total_sessions: number;
  conversion_rate: number;
}

interface ConversionMetricsProps {
  analysisId: number;
  apiUrl?: string;
}

export const ConversionMetrics: React.FC<ConversionMetricsProps> = ({
  analysisId,
  apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.funnelanalyzerpro.com',
}) => {
  const [stats, setStats] = useState<ConversionStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchConversionStats();
  }, [analysisId]);

  const fetchConversionStats = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${apiUrl}/api/reports/${analysisId}/conversions`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch conversion stats');
      }
      
      const data = await response.json();
      setStats(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching conversion stats:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md border border-gray-200 p-12">
        <div className="flex flex-col items-center justify-center text-gray-500">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mb-4"></div>
          <p>Loading conversion metrics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md border border-gray-200 p-12">
        <div className="flex flex-col items-center justify-center text-red-600">
          <FiAlertCircle className="w-12 h-12 mb-4" />
          <p className="font-semibold">Error Loading Metrics</p>
          <p className="text-sm text-gray-600 mt-2">{error}</p>
        </div>
      </div>
    );
  }

  if (!stats || stats.total_sessions === 0) {
    return (
      <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg border border-purple-200 p-12">
        <div className="text-center">
          <FiUsers className="w-16 h-16 text-purple-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Sessions Yet</h3>
          <p className="text-gray-600 mb-4">
            Install the tracking script to start capturing funnel sessions
          </p>
          <p className="text-sm text-gray-500">
            Metrics will appear here once visitors land on your funnel pages
          </p>
        </div>
      </div>
    );
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatPercent = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  // Get attribution method labels
  const getMethodLabel = (method: string): string => {
    const labels: Record<string, string> = {
      'email': 'Email Match',
      'order_id': 'Order ID',
      'session_fingerprint': 'Session ID',
      'user_id': 'User ID',
      'probabilistic': 'Probabilistic',
      'none': 'Not Attributed',
    };
    return labels[method] || method;
  };

  // Get method confidence color
  const getMethodColor = (method: string): string => {
    const colors: Record<string, string> = {
      'email': 'bg-green-500',
      'order_id': 'bg-green-600',
      'session_fingerprint': 'bg-blue-500',
      'user_id': 'bg-blue-600',
      'probabilistic': 'bg-yellow-500',
      'none': 'bg-gray-400',
    };
    return colors[method] || 'bg-gray-400';
  };

  return (
    <div className="space-y-6">
      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Revenue */}
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <div className="p-2 bg-green-100 rounded-lg">
              <FiDollarSign className="w-5 h-5 text-green-600" />
            </div>
            <span className="text-xs text-gray-500">Revenue</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {formatCurrency(stats.total_revenue)}
          </div>
          <p className="text-sm text-gray-600 mt-1">
            {stats.total_conversions} {stats.total_conversions === 1 ? 'conversion' : 'conversions'}
          </p>
        </div>

        {/* Conversion Rate */}
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <div className="p-2 bg-blue-100 rounded-lg">
              <FiTrendingUp className="w-5 h-5 text-blue-600" />
            </div>
            <span className="text-xs text-gray-500">Conv. Rate</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {formatPercent(stats.conversion_rate)}
          </div>
          <p className="text-sm text-gray-600 mt-1">
            {stats.total_sessions} sessions
          </p>
        </div>

        {/* Attribution Rate */}
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <div className="p-2 bg-purple-100 rounded-lg">
              <FiTarget className="w-5 h-5 text-purple-600" />
            </div>
            <span className="text-xs text-gray-500">Attribution</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {formatPercent(stats.attribution_rate)}
          </div>
          <p className="text-sm text-gray-600 mt-1">
            {stats.attributed_conversions} of {stats.total_conversions} matched
          </p>
        </div>

        {/* Average Confidence */}
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <div className="p-2 bg-orange-100 rounded-lg">
              <FiUsers className="w-5 h-5 text-orange-600" />
            </div>
            <span className="text-xs text-gray-500">Confidence</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {stats.avg_confidence ? formatPercent(stats.avg_confidence) : 'N/A'}
          </div>
          <p className="text-sm text-gray-600 mt-1">
            Average attribution confidence
          </p>
        </div>
      </div>

      {/* Attribution Breakdown */}
      <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
        <h3 className="font-semibold text-gray-900 mb-4">Attribution Methods</h3>
        
        {Object.keys(stats.attribution_methods).length > 0 ? (
          <div className="space-y-3">
            {Object.entries(stats.attribution_methods)
              .sort(([, a], [, b]) => b - a)
              .map(([method, count]) => {
                const percentage = (count / stats.total_conversions) * 100;
                return (
                  <div key={method}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-700">
                        {getMethodLabel(method)}
                      </span>
                      <span className="text-sm text-gray-600">
                        {count} ({formatPercent(percentage)})
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${getMethodColor(method)}`}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
          </div>
        ) : (
          <p className="text-gray-600 text-center py-4">
            No conversions recorded yet
          </p>
        )}
      </div>

      {/* Insights */}
      {stats.attribution_rate < 80 && stats.total_conversions > 5 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <FiAlertCircle className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" />
            <div>
              <h4 className="font-semibold text-yellow-900 text-sm mb-1">
                Improve Attribution Rate
              </h4>
              <p className="text-sm text-yellow-800">
                {stats.attribution_rate < 50 ? (
                  <>
                    Your attribution rate is low. Try passing <code className="bg-yellow-100 px-1 rounded">session_id</code> through
                    your checkout process, or ensure the tracking script captures email addresses at opt-in.
                  </>
                ) : (
                  <>
                    Good attribution! You can improve further by implementing order ID tracking
                    or ensuring session IDs are passed through your checkout.
                  </>
                )}
              </p>
            </div>
          </div>
        </div>
      )}

      {stats.attribution_rate >= 90 && stats.total_conversions > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <FiTarget className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
            <div>
              <h4 className="font-semibold text-green-900 text-sm mb-1">
                Excellent Attribution! 🎉
              </h4>
              <p className="text-sm text-green-800">
                Your tracking is working great! {formatPercent(stats.attribution_rate)} of conversions
                are successfully matched to sessions, giving you reliable funnel analytics.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
