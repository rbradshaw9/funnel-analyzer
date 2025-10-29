# Authentication Testing & Setup Guide

## Current Architecture

- **Backend (FastAPI)**: Deployed on Railway
- **Frontend (Next.js)**: Deployed on Vercel at funnelanalyzerpro.com  
- **Problem**: Old jQuery admin interface is being served at `/admin` instead of Next.js admin

## Issues Found

1. ✅ **Backend Authentication**: Working correctly after asyncpg timestamp fix (commit 9a3d55b)
2. ❌ **Old Admin Interface**: `/admin` path serves outdated jQuery-based static files
3. ❌ **Routing**: `funnelanalyzerpro.com/api/*` needs to proxy to Railway backend
4. ⚠️ **Environment Variables**: Railway needs `DEFAULT_ADMIN_EMAIL` and `DEFAULT_ADMIN_PASSWORD` set

## Railway Environment Variables Needed

Add these to Railway project settings:

```bash
DEFAULT_ADMIN_EMAIL=ryan@funnelanalyzerpro.com
DEFAULT_ADMIN_PASSWORD=FiR43Tx2-
DEFAULT_ADMIN_NAME="Funnel Analyzer Admin"
```

## Testing Steps

### 1. Test Backend Directly (Railway)

Find your Railway backend URL in the Railway dashboard (e.g., `https://yourapp.up.railway.app`), then:

```bash
# Test admin login
curl -X POST https://YOUR_RAILWAY_URL/api/auth/admin/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ryan@funnelanalyzerpro.com",
    "password": "FiR43Tx2-"
  }'

# Expected response:
# {
#   "token": "eyJ...",
#   "refresh_token": "eyJ...",
#   "user": {
#     "id": 1,
#     "email": "ryan@funnelanalyzerpro.com",
#     "role": "admin",
#     ...
#   }
# }
```

### 2. Test Regular User Registration

```bash
curl -X POST https://YOUR_RAILWAY_URL/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "full_name": "Test User"
  }'
```

### 3. Test Member Login

```bash
curl -X POST https://YOUR_RAILWAY_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'
```

## Frontend Authentication Flow

### Next.js Admin Dashboard

The Next.js admin dashboard exists at `frontend/app/admin/page.tsx` and requires:

1. User navigates to `https://funnelanalyzerpro.com/`
2. Login with admin credentials through the Next.js UI
3. Token stored in localStorage as `faAuthToken`
4. Admin dashboard accessible within the Next.js app

### Old Admin Interface (PROBLEM)

- **URL**: `https://funnelanalyzerpro.com/admin`
- **Technology**: jQuery 3.2.1, static files
- **Issue**: Tries to `GET /admin/env/` which doesn't exist
- **Solution**: Remove this deployment or update Vercel routing

## Fixing the /admin Path

### Option 1: Update Vercel Routing (Recommended)

Update `frontend/vercel.json` to ensure `/admin` serves the Next.js app:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://YOUR_RAILWAY_URL/api/:path*"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Frame-Options",
          "value": "SAMEORIGIN"
        }
      ]
    }
  ]
}
```

### Option 2: Remove Old Admin Deployment

1. Go to Vercel dashboard
2. Check if there's a separate project serving the old admin
3. Delete or disable that project
4. Ensure only the Next.js frontend is deployed

## Vercel Frontend Configuration

The Next.js frontend needs these environment variables:

```bash
NEXT_PUBLIC_API_URL=https://YOUR_RAILWAY_URL
```

Update in Vercel project settings → Environment Variables.

## Complete Authentication Workflow

### Admin Login:
1. Navigate to `https://funnelanalyzerpro.com`
2. Click "Admin" or "Login" in navigation
3. Enter credentials:
   - Email: `ryan@funnelanalyzerpro.com`
   - Password: `FiR43Tx2-`
4. Backend POST to `/api/auth/admin/login`
5. Store JWT token in localStorage
6. Redirect to admin dashboard

### Regular User Registration & Login:
1. Navigate to `https://funnelanalyzerpro.com`
2. Click "Sign Up"
3. Fill in registration form
4. Backend POST to `/api/auth/register`
5. Auto-login or redirect to login page
6. Login with credentials
7. Backend POST to `/api/auth/login` (member endpoint)
8. Store JWT token
9. Access user dashboard

## Common Issues & Solutions

### Issue: "We could not verify your session token"
- **Cause**: Old admin interface at `/admin` trying to use different token format
- **Solution**: Don't use `/admin` - access admin through main Next.js app

### Issue: 404 on `/admin/env/`
- **Cause**: Old admin interface trying to fetch config endpoint that doesn't exist
- **Solution**: Remove old admin deployment

### Issue: CORS errors
- **Cause**: Frontend calling backend without proper CORS setup
- **Solution**: Backend already configured for `funnelanalyzerpro.com` - ensure API proxy is set up in Vercel

### Issue: "Invalid email or password"
- **Cause**: Admin user not created on Railway
- **Solution**: Set `DEFAULT_ADMIN_EMAIL` and `DEFAULT_ADMIN_PASSWORD` environment variables in Railway

## Next Steps

1. **Set Railway Environment Variables**
   - Add admin credentials to Railway project
   - Redeploy backend to pick up env vars

2. **Find Railway Backend URL**
   - Go to Railway dashboard
   - Copy the public URL for your backend service
   - Update `NEXT_PUBLIC_API_URL` in Vercel

3. **Test Backend Authentication**
   - Use curl commands above with your Railway URL
   - Confirm admin login works
   - Confirm user registration works

4. **Fix Frontend Routing**
   - Update Vercel configuration
   - Remove old admin deployment if it exists
   - Test login through Next.js app

5. **Verify End-to-End Flow**
   - Register a test user through the frontend
   - Login as that user
   - Login as admin
   - Verify all features work

## Support

If you continue to have issues:
1. Share Railway deployment logs
2. Share Vercel deployment URL structure
3. Share browser Network tab showing failed requests
4. Confirm environment variables are set correctly
