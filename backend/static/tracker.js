/**
 * Funnel Analyzer Tracker (FATracker)
 * 
 * Client-side tracking script for funnel session monitoring and conversion attribution.
 * 
 * Usage:
 *   <script src="https://api.funnelanalyzerpro.com/tracker.js"></script>
 *   <script>
 *     FATracker.init({
 *       analysisId: YOUR_ANALYSIS_ID,
 *       apiUrl: 'https://api.funnelanalyzerpro.com',
 *       captureEmail: true, // Auto-capture email from forms
 *       trackClicks: true   // Track CTA clicks
 *     });
 *   </script>
 */

(function(window) {
  'use strict';

  const FATracker = {
    config: {
      analysisId: null,
      apiUrl: null,
      captureEmail: true,
      trackClicks: true,
      debug: false,
    },
    
    sessionId: null,
    fingerprint: null,
    initialized: false,

    /**
     * Initialize the tracker
     */
    init: function(options) {
      if (this.initialized) {
        this.log('Already initialized');
        return;
      }

      // Merge options with defaults
      this.config = Object.assign({}, this.config, options);

      if (!this.config.analysisId) {
        console.error('FATracker: analysisId is required');
        return;
      }

      if (!this.config.apiUrl) {
        console.error('FATracker: apiUrl is required');
        return;
      }

      // Generate or restore session ID
      this.sessionId = this._getOrCreateSessionId();
      
      // Generate device fingerprint
      this.fingerprint = this._generateFingerprint();

      // Create initial session
      this._createSession();

      // Track page view
      this._trackPageView();

      // Set up event listeners
      if (this.config.trackClicks) {
        this._setupClickTracking();
      }

      if (this.config.captureEmail) {
        this._setupEmailCapture();
      }

      this.initialized = true;
      this.log('Initialized', {
        sessionId: this.sessionId,
        fingerprint: this.fingerprint,
        analysisId: this.config.analysisId
      });
    },

    /**
     * Get or create a session ID (persisted in sessionStorage)
     */
    _getOrCreateSessionId: function() {
      let sessionId = sessionStorage.getItem('fa_session_id');
      
      if (!sessionId) {
        sessionId = 'fa_' + this._generateUUID();
        sessionStorage.setItem('fa_session_id', sessionId);
      }
      
      return sessionId;
    },

    /**
     * Generate a simple UUID v4
     */
    _generateUUID: function() {
      return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
      });
    },

    /**
     * Generate device fingerprint from browser data
     */
    _generateFingerprint: function() {
      const components = [
        navigator.userAgent,
        screen.width + 'x' + screen.height,
        new Date().getTimezoneOffset(),
        navigator.language,
        screen.colorDepth
      ];
      
      // Simple hash function
      const str = components.join('|');
      let hash = 0;
      for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32bit integer
      }
      
      return 'fp_' + Math.abs(hash).toString(16);
    },

    /**
     * Get URL parameters
     */
    _getUrlParams: function() {
      const params = new URLSearchParams(window.location.search);
      return {
        utm_source: params.get('utm_source'),
        utm_medium: params.get('utm_medium'),
        utm_campaign: params.get('utm_campaign'),
        utm_content: params.get('utm_content'),
        utm_term: params.get('utm_term'),
      };
    },

    /**
     * Create or update session on backend
     */
    _createSession: function() {
      const utmParams = this._getUrlParams();
      
      const sessionData = {
        session_id: this.sessionId,
        fingerprint: this.fingerprint,
        landing_page: window.location.href,
        referrer: document.referrer || null,
        screen_resolution: screen.width + 'x' + screen.height,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        language: navigator.language,
        ...utmParams
      };

      this._sendRequest('/track/' + this.config.analysisId + '/session', sessionData);
    },

    /**
     * Track a page view
     */
    _trackPageView: function() {
      this._trackEvent('pageview', {
        page_url: window.location.href,
        page_title: document.title
      });
    },

    /**
     * Track an event
     */
    _trackEvent: function(eventType, metadata) {
      const eventData = {
        session_id: this.sessionId,
        event_type: eventType,
        page_url: window.location.href,
        metadata: metadata || {}
      };

      this._sendRequest('/track/' + this.config.analysisId + '/event', eventData);
    },

    /**
     * Set up click tracking for CTAs and links
     */
    _setupClickTracking: function() {
      const self = this;
      
      document.addEventListener('click', function(e) {
        const target = e.target.closest('a, button, [data-fa-track]');
        
        if (!target) return;

        const metadata = {
          element_type: target.tagName.toLowerCase(),
          element_id: target.id || null,
          element_class: target.className || null,
          element_text: target.textContent.substring(0, 100),
          href: target.href || null,
        };

        self._trackEvent('click', metadata);
      }, true);
    },

    /**
     * Set up email capture from form inputs
     */
    _setupEmailCapture: function() {
      const self = this;
      
      // Listen for form submissions
      document.addEventListener('submit', function(e) {
        const form = e.target;
        const emailInput = form.querySelector('input[type="email"], input[name*="email"]');
        
        if (emailInput && emailInput.value) {
          self.setEmail(emailInput.value);
        }
      }, true);

      // Also capture on blur (when user leaves email field)
      document.addEventListener('blur', function(e) {
        const input = e.target;
        
        if (input.type === 'email' || input.name.toLowerCase().includes('email')) {
          if (input.value && self._isValidEmail(input.value)) {
            self.setEmail(input.value);
          }
        }
      }, true);
    },

    /**
     * Validate email format
     */
    _isValidEmail: function(email) {
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    },

    /**
     * Update session with email (when captured at opt-in)
     */
    setEmail: function(email) {
      if (!this._isValidEmail(email)) {
        this.log('Invalid email format:', email);
        return;
      }

      this.log('Email captured:', email);

      const sessionData = {
        session_id: this.sessionId,
        email: email
      };

      this._sendRequest('/track/' + this.config.analysisId + '/session', sessionData);
    },

    /**
     * Update session with order ID (for passing through checkout)
     */
    setOrderId: function(orderId) {
      this.log('Order ID set:', orderId);

      const sessionData = {
        session_id: this.sessionId,
        order_id: orderId
      };

      this._sendRequest('/track/' + this.config.analysisId + '/session', sessionData);
    },

    /**
     * Update session with user ID (for authenticated users)
     */
    setUserId: function(userId) {
      this.log('User ID set:', userId);

      const sessionData = {
        session_id: this.sessionId,
        user_id: userId
      };

      this._sendRequest('/track/' + this.config.analysisId + '/session', sessionData);
    },

    /**
     * Get current session ID (useful for passing to checkout)
     */
    getSessionId: function() {
      return this.sessionId;
    },

    /**
     * Send request to API
     */
    _sendRequest: function(endpoint, data) {
      const url = this.config.apiUrl + '/api' + endpoint;
      
      fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
        keepalive: true // Ensure request completes even if page unloads
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('HTTP ' + response.status);
        }
        return response.json();
      })
      .then(data => {
        this.log('Request success:', endpoint, data);
      })
      .catch(error => {
        this.log('Request error:', endpoint, error.message);
      });
    },

    /**
     * Debug logging
     */
    log: function() {
      if (this.config.debug) {
        console.log('[FATracker]', ...arguments);
      }
    }
  };

  // Export to window
  window.FATracker = FATracker;

})(window);
