# Admin User Seeding

This directory contains a script to seed the admin user in the production database.

## Quick Start (Railway)

Run this as a **one-time job** on Railway to create the admin account:

```bash
python backend/seed_admin.py
```

## Environment Variables

The script uses these environment variables:

- `DATABASE_URL` - PostgreSQL connection string (automatically set by Railway)
- `DEFAULT_ADMIN_EMAIL` - Admin email (default: `ryan@funnelanalyzerpro.com`)
- `DEFAULT_ADMIN_PASSWORD` - Admin password (default: `FiR43Tx2-`)

## How to Run on Railway

### Method 1: One-Time Deployment Job

1. Go to Railway Dashboard → Your Project → Backend Service
2. Click **Settings** tab
3. Scroll to **Deploy** section
4. Under **Custom Start Command**, temporarily set:
   ```
   python backend/seed_admin.py && gunicorn ...
   ```
5. Click **Deploy** - this will run the seed script once on startup
6. After successful deployment, **remove the seed command** and redeploy with just the normal start command

### Method 2: Railway CLI (Recommended)

If you have Railway CLI installed:

```bash
# Connect to Railway
railway link

# Run the seed script
railway run python backend/seed_admin.py
```

### Method 3: Manual Database Access

If the script doesn't work, you can manually create the admin user via Railway's PostgreSQL console:

1. Go to Railway Dashboard → PostgreSQL service → Data tab
2. Run this SQL (replace password hash with result from `backend.services.passwords.hash_password("FiR43Tx2-")`):

```sql
INSERT INTO users (email, role, password_hash, is_active, email_verified, plan, created_at, updated_at)
VALUES (
  'ryan@funnelanalyzerpro.com',
  'admin',
  '$2b$12$VAtsjkWhjOLiyqMBt1oMAOK...', -- Your hashed password here
  true,
  true,
  'pro',
  NOW(),
  NOW()
);
```

## Verification

After running the script, you should see:

```
✅ VERIFICATION PASSED
==========================================
Admin account is ready!
Email: ryan@funnelanalyzerpro.com
Password: FiR43Tx2-
==========================================
```

Then test logging in at https://funnelanalyzerpro.com/admin

## Troubleshooting

If you get errors:

1. **"User already exists"** - Good! The admin is already set up. Script will verify it's configured correctly.

2. **Database connection errors** - Check that `DATABASE_URL` is set correctly in Railway environment variables.

3. **bcrypt import errors** - Make sure `bcrypt` is in `requirements.txt` and Railway has built the dependencies correctly.

4. **500 errors when logging in** - Run this seed script to ensure the admin user exists with the correct password hash.

## Local Testing

To test locally (uses SQLite):

```bash
cd /path/to/funnel-analyzer
python backend/seed_admin.py
```

For local testing with PostgreSQL, set `DATABASE_URL` before running:

```bash
export DATABASE_URL="postgresql://user:pass@localhost/dbname"
python backend/seed_admin.py
```
