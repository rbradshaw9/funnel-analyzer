# Email and Admin Setup - Quick Reference

## Email Configuration

### SendGrid Setup
All transactional emails now send from **ryan@funnelanalyzerpro.com** with professional HTML templates.

**Environment Variables Required:**
```bash
SENDGRID_API_KEY=your_sendgrid_api_key_here
EMAIL_DEFAULT_FROM="Ryan at Funnel Analyzer Pro <ryan@funnelanalyzerpro.com>"
EMAIL_DEFAULT_REPLY_TO="ryan@funnelanalyzerpro.com"
```

Make sure these are set in Railway environment variables.

### Email Types

**1. Magic Link Login**
- Professional gradient header
- Clear security messaging
- Expires in 30 minutes
- Mobile-responsive design

**2. Welcome Email**
- Personalized greeting
- Plan benefits highlighted
- Getting started steps
- Dashboard access link

**3. Analysis Complete**
- Score display with emoji
- Top priority issue
- Links to full analysis
- Actionable next steps

**4. Password Reset**
- Secure reset link
- 30-minute expiration
- Clear instructions

All emails include:
- Both HTML and plain text versions
- Professional branding with Funnel Analyzer Pro colors
- Clear call-to-action buttons
- Support contact information
- Mobile-responsive design

## Admin Interface

### Admin Login
**URL:** https://funnelanalyzerpro.com/admin

**Credentials:**
- Email: ryan@funnelanalyzerpro.com
- Password: FiR43Tx2-

### Admin Features

**Dashboard Statistics:**
- Total users
- Active users  
- Users by plan (Free, Basic, Pro)
- Total analyses count
- Analyses today

**User Management:**
- **Search** - Find users by email or name
- **Filter** - By plan, status, or role
- **View Details** - Full user information
- **Delete Users** - Remove test accounts (protects admins)
- **Reset Passwords** - Admin can reset any user's password

**Security:**
- Only users with `role="admin"` can access
- Cannot delete your own account
- Cannot delete other admin accounts
- All admin actions are logged

### API Endpoints

All admin endpoints require `Authorization: Bearer <jwt_token>` header with admin role.

**GET /api/admin/stats**
- Platform statistics

**GET /api/admin/users**
- List all users
- Query params: `plan`, `status`, `role`, `search`, `skip`, `limit`

**GET /api/admin/users/{user_id}**
- Detailed user information

**PATCH /api/admin/users/{user_id}**
- Update user (plan, status, role, etc.)

**DELETE /api/admin/users/{user_id}**
- Delete user and all their data

**POST /api/admin/users/{user_id}/reset-password**
- Reset user password

## Creating Additional Admin Users

Run the initialization script:

```bash
cd /path/to/funnel-analyzer
python init_admin.py --email new.admin@example.com --password SecurePass123 --name "New Admin"
```

Or use the default (ryan@funnelanalyzerpro.com):
```bash
python init_admin.py
```

## Deleting Test Users

1. Login to https://funnelanalyzerpro.com/admin
2. Use filters to find test accounts
3. Click "Delete" next to the user
4. Confirm deletion

Note: Cannot delete admin users for safety.

## Email Template Customization

Email templates are in: `backend/services/email_templates.py`

Each template function returns:
```python
{
    "subject": "Email Subject",
    "html": "HTML version",
    "text": "Plain text version"
}
```

To customize:
1. Edit the template in `email_templates.py`
2. Commit and push to trigger deployment
3. Railway and Vercel will auto-deploy

## Troubleshooting

**Emails not sending?**
1. Check Railway environment has `SENDGRID_API_KEY`
2. Verify sender email in SendGrid dashboard
3. Check Railway logs for email errors

**Can't access admin page?**
1. Verify you're logged in with admin account
2. Check JWT token includes `role: "admin"`
3. Run `init_admin.py` to ensure admin exists

**Database shows old email sender?**
1. Update Railway environment variable `EMAIL_DEFAULT_FROM`
2. Restart Railway deployment
3. New emails will use updated sender

## Production Checklist

- [x] SendGrid API key configured in Railway
- [x] Email sender verified in SendGrid
- [x] Admin user created (ryan@funnelanalyzerpro.com)
- [x] Professional email templates deployed
- [x] Admin interface accessible at /admin
- [ ] Test magic link email delivery
- [ ] Test welcome email on new signup
- [ ] Test admin user management features

## Next Steps

1. **Test Email Delivery**
   - Request a magic link from login
   - Sign up a test user
   - Verify emails arrive with professional design

2. **Clean Up Test Users**
   - Login to /admin
   - Filter by creation date or email pattern
   - Delete test accounts

3. **Monitor Email Deliverability**
   - Check SendGrid dashboard for delivery stats
   - Watch for bounces or spam reports
   - Ensure SPF/DKIM records are configured

4. **Optional Enhancements**
   - Add email templates for subscription changes
   - Add analysis summary email option
   - Add team invitation emails (if adding team features)
