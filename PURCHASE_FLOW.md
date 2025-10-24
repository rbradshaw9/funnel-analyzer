# Purchase to Dashboard Flow - Complete Guide

## Overview

This document describes the complete user journey from purchasing on ThriveCart to accessing the Funnel Analyzer dashboard.

## Flow Diagram

```
ThriveCart Purchase
       ↓
  Webhook Sent (order.success)
       ↓
Backend Receives Webhook
       ↓
User Account Created/Updated
   ├→ Email: customer email
   ├→ Plan: basic/pro (from product name)
   ├→ Status: active
   ├→ Subscription ID
   └→ Customer ID
       ↓
Magic Link Email Sent (if email configured)
       ↓
User Clicks Magic Link
       ↓
Redirect to /dashboard?token=JWT_TOKEN
       ↓
Frontend Validates Token
       ↓
Dashboard Loads with User Data
```

## Backend Components

### 1. Webhook Handler (`backend/routes/webhooks.py`)

**Endpoint**: `POST /api/webhooks/thrivecart`

**What it does**:
- Validates webhook signature (optional, checks payload secret)
- Stores raw webhook event in database
- Calls `apply_thrivecart_membership_update()` to create/update user
- Sends magic link onboarding email if user just activated

**Test it**:
```bash
python test_purchase_flow.py
```

### 2. Subscription Service (`backend/services/subscriptions.py`)

**Function**: `apply_thrivecart_membership_update()`

**What it does**:
- Extracts customer email from webhook payload
- Creates new user or updates existing user
- Sets user status to "active" for order.success events
- Extracts plan from product name (basic/pro)
- Stores subscription_id and customer_id
- Returns `MembershipUpdateResult` with just_activated flag

**Plan Mapping**:
- Product name contains "basic" → plan = "basic"
- Product name contains "pro" or "growth" → plan = "pro"
- Otherwise → plan = "member"

### 3. Onboarding Service (`backend/services/onboarding.py`)

**Function**: `send_magic_link_onboarding()`

**What it does**:
- Generates JWT token with user_id and email
- Creates magic link: `{FRONTEND_URL}/dashboard?token={JWT}`
- Sends email with magic link button
- Updates user.last_magic_link_sent_at timestamp

**Email Template**:
- Subject: "Welcome to Funnel Analyzer Pro"
- Contains dashboard access button
- Includes plan information
- Link expires in 30 minutes (configurable)

### 4. Email Service (`backend/services/email.py`)

**What it does**:
- Wraps SendGrid API
- Sends transactional emails
- Requires SENDGRID_API_KEY in environment

**Configuration**:
```bash
# .env
SENDGRID_API_KEY=SG.your-sendgrid-api-key
EMAIL_DEFAULT_FROM="Funnel Analyzer <noreply@funnelanalyzerpro.com>"
EMAIL_DEFAULT_REPLY_TO=support@funnelanalyzerpro.com
```

### 5. Auth Service (`backend/services/auth.py`)

**Function**: `create_magic_link_token()`

**What it does**:
- Creates JWT with user_id, email, token_type="magic_link"
- Expires in MAGIC_LINK_EXPIRATION_MINUTES (default: 30)
- Signs with JWT_SECRET

**Function**: `validate_jwt_token()`

**What it does**:
- Verifies JWT signature
- Checks expiration
- Returns user_id and email if valid

## Frontend Components

### 1. Dashboard Page (`frontend/app/dashboard/page.tsx`)

**What it does**:
- Uses `useAuthValidation` hook to get token from URL
- Validates token with backend
- Shows user info, plan, status
- Displays analysis form if access granted
- Shows upgrade prompt if access denied

### 2. Auth Validation Hook (`frontend/hooks/useAuthValidation.ts`)

**What it does**:
- Extracts token from URL query parameter
- Calls `/api/auth/validate` to validate token
- Stores auth state in Zustand store
- Returns user info, access status, plan, etc.

### 3. Auth Store (`frontend/store/authStore.ts`)

**What it stores**:
- token: JWT from magic link
- auth: Full auth response with user data
- loading: Validation in progress
- error: Validation error message

## Database Schema

### User Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    plan VARCHAR(50) DEFAULT 'free',
    status VARCHAR(50) DEFAULT 'active',
    is_active INTEGER DEFAULT 1,
    status_reason VARCHAR(255),
    status_last_updated DATETIME,
    subscription_id VARCHAR(150),
    thrivecart_customer_id VARCHAR(150),
    access_expires_at DATETIME,
    portal_update_url VARCHAR(2048),
    last_magic_link_sent_at DATETIME,
    password_hash VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);
```

### WebhookEvent Table

```sql
CREATE TABLE webhook_events (
    id INTEGER PRIMARY KEY,
    source VARCHAR(100) NOT NULL,
    event_type VARCHAR(150),
    payload JSON NOT NULL,
    raw_payload TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Environment Variables Required

### Backend (.env)

```bash
# Core Auth
JWT_SECRET=your-secret-key-change-in-production
MAGIC_LINK_EXPIRATION_MINUTES=30
FRONTEND_URL=http://localhost:3001

# ThriveCart
THRIVECART_WEBHOOK_SECRET=TK432YH7UTR9

# Email (SendGrid)
SENDGRID_API_KEY=SG.your-api-key
EMAIL_DEFAULT_FROM="Funnel Analyzer <noreply@funnelanalyzerpro.com>"
EMAIL_DEFAULT_REPLY_TO=support@funnelanalyzerpro.com

# Database
DATABASE_URL=sqlite:///./funnel_analyzer.db
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:3000
NEXT_PUBLIC_JOIN_URL=https://funnelanalyzerpro.com/pricing
```

## Testing the Flow

### 1. Local Test (Without Email)

```bash
# Start backend
cd backend
source ../.venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 3000

# Start frontend
cd frontend
npm run dev

# Run test script
python test_purchase_flow.py
```

**Expected Result**:
- ✅ Webhook returns 200 OK
- ✅ User created with ID and plan
- ⚠️  Email skipped (SendGrid not configured)

### 2. With SendGrid Configured

After adding SENDGRID_API_KEY to .env:

```bash
# Restart backend to pick up new env var
pkill -f uvicorn
uvicorn backend.main:app --host 0.0.0.0 --port 3000

# Run test
python test_purchase_flow.py
```

**Expected Result**:
- ✅ Webhook returns 200 OK  
- ✅ User created
- ✅ Email sent to test-buyer@example.com
- Check SendGrid dashboard for delivery

### 3. Manual Magic Link Test

If emails aren't working, you can generate a token manually:

```bash
# In Python shell with backend running
from backend.services.auth import create_magic_link_token
token = await create_magic_link_token(user_id=1, email="test@example.com")
print(f"http://localhost:3001/dashboard?token={token}")
```

### 4. ThriveCart Integration Test

1. Go to ThriveCart → Settings → Webhooks
2. Add webhook URL: `https://your-railway-url.railway.app/api/webhooks/thrivecart`
3. Enable "Order Success" event
4. Make test purchase
5. Check webhook logs in ThriveCart dashboard

## Production Deployment Checklist

### Railway (Backend)

1. Add environment variables:
   - `JWT_SECRET` (generate strong random string)
   - `THRIVECART_WEBHOOK_SECRET=TK432YH7UTR9`
   - `SENDGRID_API_KEY=SG.your-api-key`
   - `EMAIL_DEFAULT_FROM=Funnel Analyzer <noreply@yourdomain.com>`
   - `FRONTEND_URL=https://your-vercel-domain.vercel.app`

2. Install SendGrid in requirements.txt:
   ```
   sendgrid>=6.12.5
   ```

3. Deploy backend

### Vercel (Frontend)

1. Add environment variable:
   - `NEXT_PUBLIC_API_URL=https://your-railway-domain.railway.app`

2. Deploy frontend

### ThriveCart Configuration

1. Go to Settings → Webhooks
2. Add webhook URL: `https://your-railway-domain.railway.app/api/webhooks/thrivecart`
3. Enable events:
   - ✅ Order Success
   - ✅ Order Refund
   - ✅ Subscription Payment
   - ✅ Subscription Canceled

4. Test webhook delivery

### SendGrid Configuration

1. Create account at sendgrid.com
2. Verify sender email domain
3. Create API key with "Mail Send" permission
4. Add to Railway environment variables

## Troubleshooting

### User Not Created

**Check**:
- Webhook received (check `/api/webhooks/thrivecart/events?secret=TK432YH7UTR9&limit=10`)
- Email in webhook payload
- Backend logs for errors

### Magic Link Not Sent

**Check**:
- SendGrid SDK installed: `pip list | grep sendgrid`
- SENDGRID_API_KEY configured
- Email service initialized: Check logs for "Initialized SendGrid"
- Backend logs for email errors

### Token Invalid

**Check**:
- JWT_SECRET same on backend and frontend
- Token not expired (30 min default)
- Token format correct (should be JWT)

### Dashboard Not Loading

**Check**:
- Frontend can reach backend API
- CORS configured correctly
- Token in URL query parameter
- Browser console for errors

## API Endpoints Reference

### POST /api/webhooks/thrivecart
- Receives ThriveCart webhooks
- No auth required (validates webhook secret)
- Returns: `{"status": "ok", "event_id": 123, "user_id": 456}`

### GET /api/webhooks/thrivecart/events
- Lists recent webhook events
- Auth: Query param `secret={THRIVECART_WEBHOOK_SECRET}`
- Returns: `{"events": [...]}`

### POST /api/auth/magic-link
- Requests magic link email
- Body: `{"email": "user@example.com"}`
- Returns: `{"status": "sent", "message": "Magic link sent"}`

### POST /api/auth/validate
- Validates JWT token
- Body: `{"token": "eyJ..."}`
- Returns: `{"valid": true, "user_id": 123, "email": "...", "plan": "basic", ...}`

## Status Mapping

### ThriveCart Events → User Status

| Event | User Status | Access Granted |
|-------|-------------|----------------|
| order.success | active | Yes |
| order.paid | active | Yes |
| subscription_payment_success | active | Yes |
| subscription_payment_failed | past_due | No |
| subscription_cancelled | canceled | No |
| order.refund | canceled | No |

## Next Steps

1. ✅ Backend webhook handling (DONE)
2. ✅ User account creation (DONE)
3. ✅ Magic link email system (DONE)
4. ✅ Dashboard with auth (DONE)
5. ⏳ Install SendGrid SDK
6. ⏳ Configure SendGrid API key
7. ⏳ Test complete flow
8. ⏳ Deploy to production
9. ⏳ Configure ThriveCart webhooks
10. ⏳ Test production purchase flow
