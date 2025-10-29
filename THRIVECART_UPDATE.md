# ThriveCart URL Update Checklist

## ✅ Completed (Local & Code)
- [x] Updated `frontend/lib/externalLinks.ts` with new URLs
- [x] Updated `frontend/.env.example`
- [x] Updated `frontend/.env.local`
- [x] Fixed `/admin` redirect loop - now shows login prompt
- [x] Committed and pushed to GitHub

## 🔄 Required: Vercel Environment Variables

You need to update these in your Vercel dashboard:

1. Go to: https://vercel.com/[your-username]/funnel-analyzer/settings/environment-variables

2. Update or add these variables:
   ```
   NEXT_PUBLIC_BASIC_CHECKOUT_URL=https://ignitiongo.thrivecart.com/funnel-analyzer-basic/
   NEXT_PUBLIC_PRO_CHECKOUT_URL=https://ignitiongo.thrivecart.com/funnel-analyzer-pro/
   ```

3. Redeploy the frontend (Vercel will auto-deploy from the git push, but you may want to verify)

## 📋 ThriveCart Configuration

Update your ThriveCart webhook settings with the correct callback URL:

**Webhook URL:**
```
https://api.funnelanalyzerpro.com/api/webhooks/thrivecart
```

**Success Page URLs** (in each product):
- Basic Plan: `https://funnelanalyzerpro.com/success?plan=basic`
- Pro Plan: `https://funnelanalyzerpro.com/success?plan=pro`

## 🧪 Testing

After Vercel deployment:

1. **Test Basic Plan Checkout:**
   - Go to https://funnelanalyzerpro.com/pricing
   - Click "Choose Basic" button
   - Should redirect to: https://ignitiongo.thrivecart.com/funnel-analyzer-basic/

2. **Test Pro Plan Checkout:**
   - Click "Choose Pro" button
   - Should redirect to: https://ignitiongo.thrivecart.com/funnel-analyzer-pro/

3. **Test Admin Login:**
   - Go to https://funnelanalyzerpro.com/admin
   - Should show login prompt (not redirect to home)
   - Click "Sign In" button
   - Login with ryan@funnelanalyzerpro.com / FiR43Tx2-
   - Should show admin dashboard

## 🔍 Admin Page Fix

The `/admin` page was redirecting to home because it checked for a token on load and redirected if not found. 

**Fixed behavior:**
- ✅ Shows professional login prompt when not authenticated
- ✅ Login button opens AuthModal
- ✅ After login, admin dashboard loads automatically
- ✅ Clear messaging about admin access requirements

## 📝 Notes

The jQuery errors (`GET /env/ 404`) you saw are unrelated - they appear to be from a browser extension trying to load environment files. They won't affect functionality.
