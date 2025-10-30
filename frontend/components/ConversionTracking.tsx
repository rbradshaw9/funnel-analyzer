/**
 * ConversionTracking Component
 * 
 * Displays tracking setup instructions and conversion metrics for a funnel analysis.
 */

'use client';

import React, { useState } from 'react';
import { FiCopy, FiCheck, FiActivity, FiTrendingUp, FiCode } from 'react-icons/fi';
import { ConversionMetrics } from './ConversionMetrics';

interface ConversionTrackingProps {
  analysisId: number;
  apiUrl?: string;
}

export const ConversionTracking: React.FC<ConversionTrackingProps> = ({
  analysisId,
  apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.funnelanalyzerpro.com',
}) => {
  const [activeTab, setActiveTab] = useState<'setup' | 'webhook' | 'stats'>('setup');
  const [copiedScript, setCopiedScript] = useState(false);
  const [copiedWebhook, setCopiedWebhook] = useState(false);

  const webhookUrl = `${apiUrl}/api/webhooks/convert/${analysisId}`;
  
  const trackingScript = `<!-- Funnel Analyzer Conversion Tracking -->
<script src="${apiUrl}/tracker.js"></script>
<script>
  FATracker.init({
    analysisId: ${analysisId},
    apiUrl: '${apiUrl}',
    captureEmail: true,
    trackClicks: true,
    debug: false
  });
</script>`;

  const webhookExample = `// Stripe webhook example
{
  "conversion_id": "pi_123456789",
  "email": "customer@example.com",
  "revenue": 97.00,
  "currency": "USD",
  "customer_name": "John Doe",
  "product_name": "Premium Package",
  "webhook_source": "stripe"
}`;

  const handleCopyScript = async () => {
    await navigator.clipboard.writeText(trackingScript);
    setCopiedScript(true);
    setTimeout(() => setCopiedScript(false), 2000);
  };

  const handleCopyWebhook = async () => {
    await navigator.clipboard.writeText(webhookUrl);
    setCopiedWebhook(true);
    setTimeout(() => setCopiedWebhook(false), 2000);
  };

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-100 rounded-lg">
            <FiActivity className="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Conversion Tracking</h2>
            <p className="text-sm text-gray-600">
              Track sessions and attribute conversions to measure funnel performance
            </p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200">
        <button
          onClick={() => setActiveTab('setup')}
          className={`px-6 py-3 font-medium text-sm transition-colors ${
            activeTab === 'setup'
              ? 'border-b-2 border-purple-600 text-purple-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <div className="flex items-center gap-2">
            <FiCode className="w-4 h-4" />
            Setup Instructions
          </div>
        </button>
        <button
          onClick={() => setActiveTab('webhook')}
          className={`px-6 py-3 font-medium text-sm transition-colors ${
            activeTab === 'webhook'
              ? 'border-b-2 border-purple-600 text-purple-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <div className="flex items-center gap-2">
            <FiTrendingUp className="w-4 h-4" />
            Webhook Setup
          </div>
        </button>
        <button
          onClick={() => setActiveTab('stats')}
          className={`px-6 py-3 font-medium text-sm transition-colors ${
            activeTab === 'stats'
              ? 'border-b-2 border-purple-600 text-purple-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <div className="flex items-center gap-2">
            <FiActivity className="w-4 h-4" />
            Metrics
          </div>
        </button>
      </div>

      {/* Content */}
      <div className="p-6">
        {activeTab === 'setup' && (
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Step 1: Install Tracking Script</h3>
              <p className="text-sm text-gray-600 mb-4">
                Add this script to every page in your funnel (just before the closing {`</body>`} tag):
              </p>
              
              <div className="relative">
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm font-mono">
                  {trackingScript}
                </pre>
                <button
                  onClick={handleCopyScript}
                  className="absolute top-3 right-3 p-2 bg-gray-800 hover:bg-gray-700 rounded-md transition-colors"
                  title="Copy to clipboard"
                >
                  {copiedScript ? (
                    <FiCheck className="w-4 h-4 text-green-400" />
                  ) : (
                    <FiCopy className="w-4 h-4 text-gray-400" />
                  )}
                </button>
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-2">What This Tracks</h3>
              <ul className="space-y-2 text-sm text-gray-700">
                <li className="flex items-start gap-2">
                  <span className="text-purple-600 mt-1">•</span>
                  <span><strong>Page views:</strong> Every page visited in your funnel</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-purple-600 mt-1">•</span>
                  <span><strong>Email capture:</strong> Automatically captures email when visitor opts in</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-purple-600 mt-1">•</span>
                  <span><strong>CTA clicks:</strong> Tracks button and link clicks throughout the funnel</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-purple-600 mt-1">•</span>
                  <span><strong>Device fingerprint:</strong> Creates unique session identifier for attribution</span>
                </li>
              </ul>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-semibold text-blue-900 mb-2 text-sm">💡 Pro Tip</h4>
              <p className="text-sm text-blue-800">
                For direct-purchase funnels (no opt-in), you can pass the session ID to your
                checkout system for 100% accurate attribution:
              </p>
              <pre className="mt-2 bg-blue-900 text-blue-100 p-3 rounded text-xs font-mono overflow-x-auto">
{`<input type="hidden" name="fa_session_id" id="fa_session_id">
<script>
  document.getElementById('fa_session_id').value = FATracker.getSessionId();
</script>`}
              </pre>
            </div>
          </div>
        )}

        {activeTab === 'webhook' && (
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Webhook URL</h3>
              <p className="text-sm text-gray-600 mb-4">
                Configure your payment processor to send conversion webhooks to this URL:
              </p>
              
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  readOnly
                  value={webhookUrl}
                  className="flex-1 px-4 py-2 bg-gray-50 border border-gray-300 rounded-lg text-sm font-mono"
                />
                <button
                  onClick={handleCopyWebhook}
                  className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors flex items-center gap-2"
                >
                  {copiedWebhook ? (
                    <>
                      <FiCheck className="w-4 h-4" />
                      Copied
                    </>
                  ) : (
                    <>
                      <FiCopy className="w-4 h-4" />
                      Copy
                    </>
                  )}
                </button>
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Webhook Payload Format</h3>
              <p className="text-sm text-gray-600 mb-4">
                Send a POST request with JSON data:
              </p>
              
              <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm font-mono">
                {webhookExample}
              </pre>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Supported Platforms</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2 text-sm">Stripe</h4>
                  <p className="text-xs text-gray-600 mb-2">
                    Configure webhook in Stripe Dashboard → Developers → Webhooks
                  </p>
                  <p className="text-xs text-gray-500">
                    Listen for: <code className="bg-gray-100 px-1 rounded">payment_intent.succeeded</code>
                  </p>
                </div>
                
                <div className="border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2 text-sm">Infusionsoft</h4>
                  <p className="text-xs text-gray-600 mb-2">
                    Set up webhook in Settings → Application → Legacy Webhooks
                  </p>
                  <p className="text-xs text-gray-500">
                    Trigger: Invoice Payment Received
                  </p>
                </div>
                
                <div className="border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2 text-sm">ThriveCart</h4>
                  <p className="text-xs text-gray-600 mb-2">
                    Add webhook URL in Product Settings → Advanced
                  </p>
                  <p className="text-xs text-gray-500">
                    Send on: Successful Purchase
                  </p>
                </div>
                
                <div className="border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2 text-sm">Manual Integration</h4>
                  <p className="text-xs text-gray-600 mb-2">
                    Send POST request from your server after conversion
                  </p>
                  <p className="text-xs text-gray-500">
                    Include email or session_id for attribution
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h4 className="font-semibold text-yellow-900 mb-2 text-sm">⚠️ Attribution Methods</h4>
              <p className="text-sm text-yellow-800 mb-2">
                The system will try to match conversions in this order:
              </p>
              <ol className="text-sm text-yellow-800 space-y-1 ml-4 list-decimal">
                <li><strong>Email match:</strong> 95% accurate for opt-in funnels</li>
                <li><strong>Order ID:</strong> 100% accurate if passed through funnel</li>
                <li><strong>Session ID:</strong> 90% accurate if sent in webhook</li>
                <li><strong>Device fingerprint:</strong> 50-70% accurate (probabilistic)</li>
              </ol>
            </div>
          </div>
        )}

        {activeTab === 'stats' && (
          <ConversionMetrics analysisId={analysisId} apiUrl={apiUrl} />
        )}
      </div>
    </div>
  );
};
