# Railway Production Deployment Checklist

## 🚀 Pre-Deployment Verification

### ✅ Code Status
- [x] All changes committed to `main` branch
- [x] Latest changes pushed to GitHub (commit `b95252f`)
- [x] All Python syntax checks pass
- [x] Type safety issues resolved
- [x] Critical business logic (product filtering) implemented

---

## 🔧 Railway Environment Variables Configuration

### Required Variables (MUST Set Before Deploy)

#### 🔑 **Critical Security**
```bash
JWT_SECRET=<generate-strong-secret-min-32-chars>
THRIVECART_WEBHOOK_SECRET=TK432YH7UTR9
```

**Generate JWT Secret:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 📧 **Email Service (SendGrid)**
```bash
SENDGRID_API_KEY=<your-sendgrid-api-key>
EMAIL_DEFAULT_FROM="Funnel Analyzer Pro <reports@funnelanalyzerpro.com>"
EMAIL_DEFAULT_REPLY_TO=support@funnelanalyzerpro.com
```

**Without SendGrid:** Magic links won't be sent (users can't login)

#### 🛒 **ThriveCart Product Filtering (CRITICAL)**
```bash
THRIVECART_BASIC_PRODUCT_IDS=["7"]
THRIVECART_PRO_PRODUCT_IDS=["8"]
```

**⚠️ IMPORTANT:** Verify these match your actual ThriveCart product IDs!

To find your product IDs:
1. Go to ThriveCart dashboard
2. Navigate to Products
3. Edit each product and check the URL or settings page

#### 🤖 **OpenAI API**
```bash
OPENAI_API_KEY=sk-proj-...
LLM_PROVIDER=openai
```

---

### Optional but Recommended

#### 🎨 **Frontend URLs**
```bash
FRONTEND_URL=https://funnelanalyzerpro.com
```

#### 📊 **Environment Settings**
```bash
ENVIRONMENT=production
DEBUG=false
```

#### 👤 **Admin Account (Optional)**
```bash
DEFAULT_ADMIN_EMAIL=admin@yourcompany.com
DEFAULT_ADMIN_PASSWORD=<strong-password>
```

Only set these if you want an admin account auto-created on first startup.

---

### Optional Integrations

#### ☁️ **Screenshot Storage (S3/R2/Supabase)**
```bash
AWS_S3_BUCKET=your-bucket-name
AWS_S3_REGION=us-east-1
AWS_S3_ACCESS_KEY_ID=...
AWS_S3_SECRET_ACCESS_KEY=...
AWS_S3_ENDPOINT_URL=https://...  # For R2/Supabase
AWS_S3_BASE_URL=https://cdn.yoursite.com  # Optional CDN
```

**Without S3:** Screenshots saved as base64 in database (works but larger DB)

#### 📨 **Mautic CRM Integration**
```bash
MAUTIC_BASE_URL=https://your-mautic.com
MAUTIC_CLIENT_ID=...
MAUTIC_CLIENT_SECRET=...
```

---

## 📝 Railway Deployment Steps

### 1. **Connect GitHub Repository**
- Go to Railway dashboard
- Click "New Project"
- Select "Deploy from GitHub repo"
- Choose `rbradshaw9/funnel-analyzer`
- Railway will auto-detect the `backend` directory

### 2. **Configure Database**
Railway will automatically provision PostgreSQL. The `DATABASE_URL` will be set automatically.

**Verify:**
- Check that `DATABASE_URL` starts with `postgresql://` (not `postgres://`)
- If it starts with `postgres://`, Railway will auto-convert it

### 3. **Set Environment Variables**
In Railway dashboard:
- Go to your project → Variables
- Add all required variables from above
- Click "Save" (Railway will redeploy)

### 4. **Configure Build Settings (if needed)**
Railway should auto-detect. If manual config needed:

**Build Command:**
```bash
pip install -r backend/requirements.txt
```

**Start Command:**
```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

**Root Directory:** `/` (Railway handles backend subfolder)

### 5. **Verify Deployment**
After deployment completes:

```bash
# Test health endpoint
curl https://your-app.railway.app/api/metrics/stats

# Should return:
{"analyses_run": 0, "pages_analyzed": 0}
```

---

## 🧪 Post-Deployment Testing

### Test 1: Webhook Endpoint
```bash
curl -X GET https://your-app.railway.app/api/webhooks/thrivecart
# Should return: {"status": "ready"}
```

### Test 2: Product Filtering (Critical!)
Send a test webhook from ThriveCart or use:

```bash
curl -X POST https://your-app.railway.app/api/webhooks/thrivecart \
  -H "Content-Type: application/json" \
  -d '{
    "thrivecart_secret": "TK432YH7UTR9",
    "event": "order.success",
    "product_id": "999",
    "customer": {"email": "test@example.com"}
  }'
```

**Expected:** Webhook accepted but NO user created (product_id=999 filtered)

Check logs for:
```
Skipping ThriveCart webhook for non-Funnel Analyzer product_id=999
```

### Test 3: Valid Product Purchase
```bash
curl -X POST https://your-app.railway.app/api/webhooks/thrivecart \
  -H "Content-Type: application/json" \
  -d '{
    "thrivecart_secret": "TK432YH7UTR9",
    "event": "order.success",
    "product_id": "7",
    "customer": {
      "email": "realuser@example.com",
      "name": "Test User"
    }
  }'
```

**Expected:** 
- User created
- Magic link email sent (if SendGrid configured)
- Check Railway logs for success

### Test 4: Magic Link Email
If SendGrid is configured:
- Trigger a real purchase or use test webhook
- Check email inbox for magic link
- Click link → should redirect to dashboard
- Verify JWT token validates

### Test 5: Database Migrations
Check Railway logs for:
```
INFO: Acquiring advisory lock for startup migrations
INFO: Ensured users.status column exists
INFO: 🚀 Starting Funnel Analyzer Pro API
```

---

## 🔍 Monitoring & Verification

### Railway Logs to Watch

**Successful Startup:**
```
INFO: 🚀 Starting Funnel Analyzer Pro API
INFO: Environment: production
INFO: Initialized SendGrid email service
```

**Product Filtering Working:**
```
INFO: Skipping ThriveCart webhook for non-Funnel Analyzer product_id=X
INFO: Created user test@example.com from ThriveCart webhook
```

**Email Delivery:**
```
INFO: Magic link sent to user@example.com
INFO: SendGrid response status: 202
```

### Health Checks

Set up Railway health check endpoint:
```
/api/metrics/stats
```

This should always return 200 with JSON.

---

## 🚨 Troubleshooting

### Issue: "No module named 'bcrypt'"
**Fix:** Add to `backend/requirements.txt` (should already be there)

### Issue: "ThriveCart secret validation failed"
**Check:**
1. `THRIVECART_WEBHOOK_SECRET` is set correctly
2. ThriveCart webhook configuration uses same secret
3. Secret in webhook payload matches env var

### Issue: "Magic links not sending"
**Check:**
1. `SENDGRID_API_KEY` is set
2. SendGrid sender email is verified
3. Railway logs for SendGrid errors

### Issue: "All products being filtered"
**Check:**
1. `THRIVECART_BASIC_PRODUCT_IDS` format: `["7"]` (JSON array)
2. Product IDs match your actual ThriveCart products
3. No extra quotes or whitespace

### Issue: "Database connection errors"
**Check:**
1. Railway PostgreSQL addon is active
2. `DATABASE_URL` is set (auto-configured)
3. Connection string format is correct

---

## 📊 Success Criteria

- [ ] Railway deployment successful (green checkmark)
- [ ] Health endpoint returns 200
- [ ] Database migrations run successfully
- [ ] Test webhook accepted (product_id=7)
- [ ] Invalid product filtered (product_id=999)
- [ ] Magic link email received (if SendGrid configured)
- [ ] User can login with magic link
- [ ] Dashboard loads for authenticated user
- [ ] No errors in Railway logs

---

## 🎯 ThriveCart Webhook Configuration

After Railway deployment:

1. **Get Railway URL:** `https://your-app.railway.app`

2. **In ThriveCart:**
   - Go to Settings → Webhooks
   - Add new webhook URL: `https://your-app.railway.app/api/webhooks/thrivecart`
   - Set secret: `TK432YH7UTR9`
   - Enable events:
     - `order.success`
     - `order.refund`
     - `subscription_cancelled`
     - `subscription_payment_failed`

3. **Test webhook** from ThriveCart admin

---

## 🔐 Security Checklist

- [ ] Strong JWT_SECRET generated (min 32 chars)
- [ ] THRIVECART_WEBHOOK_SECRET matches ThriveCart config
- [ ] SendGrid API key is restricted (not full access)
- [ ] Database uses strong password (Railway auto-generates)
- [ ] No secrets in git repository
- [ ] HTTPS only (Railway provides automatically)
- [ ] CORS configured for production frontend URL

---

## 📈 Next Steps After Deployment

1. **Monitor first 24 hours** for any errors
2. **Test real purchase flow** end-to-end
3. **Verify refund/cancellation** events work
4. **Set up error alerting** (Railway Slack/email integration)
5. **Document production URLs** for team
6. **Update frontend** `NEXT_PUBLIC_API_URL` to Railway URL

---

## 🆘 Support Contacts

**Railway Support:** https://railway.app/help  
**ThriveCart Support:** https://support.thrivecart.com  
**SendGrid Support:** https://support.sendgrid.com

---

**Deployment Status:** Ready ✅  
**Last Updated:** October 27, 2025  
**Latest Commit:** `b95252f` (product filtering + audit fixes)
