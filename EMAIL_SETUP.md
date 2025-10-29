# Email Results Setup Guide

## Issue: Emails Not Being Sent

When you enter an email in the "Optional: Email results to this address" field, no email is received.

## Root Cause

The backend requires **SendGrid** to be configured to send emails. Without SendGrid API credentials, the email service is disabled.

## Solution: Configure SendGrid

### Step 1: Get SendGrid API Key

1. Go to [SendGrid.com](https://sendgrid.com) and create a free account
2. Navigate to **Settings** → **API Keys**
3. Click **Create API Key**
4. Name it: `Funnel Analyzer Production`
5. Choose **Full Access** permissions
6. Click **Create & View**
7. **COPY THE API KEY NOW** (you won't see it again)

### Step 2: Add to Railway Environment Variables

1. Go to Railway Dashboard → Your Project → Variables
2. Add these environment variables:

```
SENDGRID_API_KEY = SG.xxxxxxxxxxxx...your-api-key
EMAIL_DEFAULT_FROM = reports@funnelanalyzerpro.com
EMAIL_DEFAULT_REPLY_TO = support@funnelanalyzerpro.com
```

3. Click **Redeploy** to apply changes

### Step 3: Verify Sender Email

SendGrid requires you to verify your sender email:

1. In SendGrid dashboard → **Settings** → **Sender Authentication**
2. Click **Verify a Single Sender**
3. Fill in:
   - From Name: `Funnel Analyzer Pro`
   - From Email: `reports@funnelanalyzerpro.com`
   - Reply To: `support@funnelanalyzerpro.com`
4. Check your email and click the verification link

**OR** (recommended for production):

1. **Authenticate Your Domain**
2. Follow SendGrid's domain authentication steps
3. Add DNS records to your domain registrar
4. This prevents emails from going to spam

---

## Testing

After configuring SendGrid:

1. Go to your frontend: `https://funnelanalyzerpro.com`
2. Start a new funnel analysis
3. Enter URLs
4. **Check the box**: "Email results to this address"
5. Enter your email
6. Click **Analyze Funnel**
7. Check your email inbox (and spam folder)

You should receive an email with:
- Subject: `Your Funnel Analyzer Pro Report (Score: XX/100)`
- Summary of the analysis
- Overall score
- Page breakdown with scores
- Link to full dashboard

---

## Alternative: Use Email Templates System

If you don't want to use SendGrid, you can use the built-in email template system:

### Option 1: Resend (Easier Setup)

Install Resend:
```bash
pip install resend
```

Update `backend/services/email.py` to use Resend instead of SendGrid.

### Option 2: SMTP (Use Any Email Provider)

Use Python's built-in `smtplib`:

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# In email.py
async def send_email(to_email, subject, html_content):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = 'reports@funnelanalyzerpro.com'
    msg['To'] = to_email
    
    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your-email@gmail.com', 'your-app-password')
        server.send_message(msg)
```

---

## Troubleshooting

### "No email received"

**Check Railway logs:**
```bash
railway logs
```

Look for:
- `SendGrid not configured. Emails disabled.` → Add SENDGRID_API_KEY
- `SendGrid SDK not installed` → Add `sendgrid` to requirements.txt
- `SendGrid response status: 202` → Email sent successfully
- `Failed to send email via SendGrid` → Check API key

### "Email goes to spam"

1. **Authenticate your domain** in SendGrid
2. Add **SPF** and **DKIM** records to your DNS
3. Use a real sender email (not no-reply@localhost)
4. Include an unsubscribe link

### "SendGrid requires payment"

SendGrid Free Plan:
- 100 emails/day forever free
- Perfect for getting started

If you need more:
- **Essentials Plan**: $19.95/month (50,000 emails)
- **Pro Plan**: $89.95/month (100,000 emails)

---

## Current State

**Email Service**: ❌ Not Configured  
**SendGrid API Key**: Missing from Railway  
**Sender Email**: Not verified  
**Email Template**: ✅ Code exists and works

**What happens now:**
- User enters email address ✅
- Backend receives the email ✅
- Email service checks for SendGrid ❌ Not found
- Logs: `"Email service unavailable; skipping analysis notification"` 
- No email sent ❌

**After configuring SendGrid:**
- User enters email address ✅
- Backend receives the email ✅
- Email service initialized with SendGrid ✅
- Email sent via SendGrid API ✅
- User receives email ✅

---

## Quick Fix Checklist

- [ ] Sign up for SendGrid (free account)
- [ ] Create API key with Full Access
- [ ] Add `SENDGRID_API_KEY` to Railway variables
- [ ] Add `EMAIL_DEFAULT_FROM` to Railway variables
- [ ] Add `EMAIL_DEFAULT_REPLY_TO` to Railway variables
- [ ] Redeploy Railway backend
- [ ] Verify sender email in SendGrid
- [ ] Test by running analysis with email address
- [ ] Check inbox (and spam folder)
- [ ] ✅ Working!

---

## Files Involved

- `backend/services/email.py` - SendGrid integration
- `backend/services/notifications.py` - Email content creation
- `backend/routes/analysis.py` - Triggers email send
- `backend/utils/config.py` - Environment variable definitions

---

## Need Help?

Check Railway logs after deploying with SendGrid configured:
```bash
railway logs | grep -i "email\|sendgrid"
```

Should see:
```
INFO - Initialized SendGrid email service
INFO - SendGrid response status: 202
```
