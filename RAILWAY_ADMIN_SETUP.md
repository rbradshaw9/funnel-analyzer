# Fix Admin Login - Set Environment Variables on Railway

## Problem
The admin user creation logic already exists in `backend/db/session.py` but requires environment variables to be set.

## Solution - Add to Railway

1. Go to **Railway Dashboard** → Your Project → **Backend Service**
2. Click **Variables** tab
3. Add these two variables:

```
DEFAULT_ADMIN_EMAIL=ryan@funnelanalyzerpro.com
DEFAULT_ADMIN_PASSWORD=FiR43Tx2-
```

4. Click **Deploy** (Railway will auto-redeploy)
5. Wait for deployment to complete (~2 minutes)
6. Try logging in at https://funnelanalyzerpro.com/admin

## What Happens

When the backend starts up, `init_db()` runs and:
- ✅ Checks if admin user exists
- ✅ If not, creates admin with email/password from env vars
- ✅ If exists, updates password to match env var
- ✅ Ensures role is "admin" and plan is "pro"

## Verification

After deployment, check Railway logs for:
```
INFO: Admin account seeding...
```

Should NOT see:
```
WARNING: Admin account seeding skipped: DEFAULT_ADMIN_EMAIL and DEFAULT_ADMIN_PASSWORD are not set.
```

## Alternative: Use the Seed Script

If you prefer not to store the password in Railway env vars permanently, you can:

1. Set the env vars temporarily
2. Let deployment create the admin user
3. Remove the env vars after successful creation
4. The admin user will persist in the database

Or use the manual seed script:
```bash
railway run python backend/seed_admin.py
```
