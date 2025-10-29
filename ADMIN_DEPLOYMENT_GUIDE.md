# Admin Interface Enhancement - Deployment Guide

## Summary of Changes

This update adds comprehensive admin management features to the Funnel Analyzer Pro platform:

### New Admin Features

1. **User Editing** - Edit user plan, status, role, and full name
2. **Subscription Details** - View subscription ID, ThriveCart customer ID, access expiration
3. **User Analyses** - View all analyses created by any user
4. **Email Template Management** - Customize transactional email templates

### Files Changed

#### Backend
- `backend/models/database.py` - Added EmailTemplate model
- `backend/routes/admin.py` - Added email template CRUD endpoints + user analyses endpoint
- `backend/scripts/add_email_templates_table.py` - Database migration script (NEW)

#### Frontend
- `frontend/app/admin/page.tsx` - Added edit button, expand/collapse rows, analyses button
- `frontend/app/admin/emails/page.tsx` - Email template management page (NEW)
- `frontend/components/UserEditModal.tsx` - User editing modal (NEW)
- `frontend/components/UserAnalysesModal.tsx` - User analyses viewer modal (NEW)

## Deployment Steps

### 1. Database Migration (Railway Backend)

The backend needs a new `email_templates` table. Railway will automatically rebuild from the Dockerfile when you push, but you need to run the migration script after deployment.

**Option A: Run migration via Railway CLI**
```bash
# After pushing to main and Railway rebuilds
railway run python -m backend.scripts.add_email_templates_table
```

**Option B: Run migration via Railway dashboard**
1. Go to Railway dashboard → Your project
2. Click on your backend service
3. Go to "Settings" → "Deploy"
4. After deployment completes, go to "Deployments"
5. Click on the latest deployment → "View Logs"
6. In a separate terminal, connect to Railway:
   ```bash
   railway link
   railway run python -m backend.scripts.add_email_templates_table
   ```

**Option C: Auto-migration on startup**
Add this to `backend/entrypoint.sh` before starting the server:
```bash
# Run migrations
python -m backend.scripts.add_email_templates_table || echo "Migration failed or already applied"
```

### 2. Frontend Deployment (Vercel)

No configuration changes needed. Vercel will automatically deploy when you push to main.

### 3. Git Deployment

```bash
# Stage all changes
git add .

# Commit with descriptive message
git commit -m "feat: Add comprehensive admin features

- User editing (plan, status, role, full name)
- Subscription details display (expandable rows)
- User analyses viewer
- Email template management system
- Backend endpoints for admin operations
- Database migration for email_templates table"

# Push to trigger deployments
git push origin main
```

### 4. Post-Deployment Verification

1. **Backend Health Check**
   ```bash
   curl https://api.funnelanalyzerpro.com/health
   ```

2. **Admin Login**
   - Go to https://funnelanalyzerpro.com/admin
   - Login with admin credentials

3. **Test User Management**
   - View user list
   - Click expand button (chevron) to see subscription details
   - Click "Edit" on a user, change their plan, save
   - Verify the change persists

4. **Test Analyses Viewer**
   - Click "Analyses" on a user with analyses
   - Verify modal shows their analysis history
   - Click "View" to open individual analysis

5. **Test Email Templates**
   - Go to https://funnelanalyzerpro.com/admin/emails
   - Select a template (e.g., "Welcome Email")
   - Click "Edit"
   - Modify the subject or content
   - Click "Save"
   - Verify template shows as "Custom"
   - Click "Preview" to see changes

## Rollback Plan

If issues occur:

### Frontend Rollback
```bash
# Revert last commit
git revert HEAD
git push origin main
```

### Backend Rollback
```bash
# If email_templates table causes issues, drop it:
railway run psql $DATABASE_URL -c "DROP TABLE IF EXISTS email_templates CASCADE;"
```

### Manual Fixes
- If migration fails: Check Railway logs for SQL errors
- If frontend breaks: Check Vercel deployment logs
- If admin access fails: Verify Railway env vars (DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD)

## New API Endpoints

### User Management
- `PATCH /api/admin/users/{user_id}` - Update user details
- `GET /api/admin/users/{user_id}` - Get detailed user info (already existed, now used for expand)
- `GET /api/admin/users/{user_id}/analyses` - Get user's analyses (NEW)

### Email Templates
- `GET /api/admin/email-templates` - List all templates (NEW)
- `GET /api/admin/email-templates/{name}` - Get specific template (NEW)
- `PUT /api/admin/email-templates/{name}` - Update/create template (NEW)
- `DELETE /api/admin/email-templates/{name}` - Delete custom template, revert to default (NEW)

## Environment Variables

No new environment variables required. Existing admin authentication uses:
- `DEFAULT_ADMIN_EMAIL`
- `DEFAULT_ADMIN_PASSWORD`
- `DEFAULT_ADMIN_NAME`

## Testing Checklist

- [ ] Admin login works
- [ ] User list displays correctly
- [ ] User expand shows subscription details
- [ ] User edit modal opens and saves changes
- [ ] User analyses modal shows analysis history
- [ ] Email templates page loads
- [ ] Email template editing and saving works
- [ ] Custom templates can be reverted to defaults
- [ ] Email template preview works
- [ ] All modals close properly
- [ ] Error handling works (try editing with invalid data)
- [ ] Non-admin users see "Access Denied" (test with regular account)

## Known Limitations

1. **Email Templates**: Changes only apply to future emails, not retroactive
2. **Database Migration**: Must be run manually on Railway (auto-migration recommended)
3. **User Analyses**: Limited to 50 most recent (can add pagination if needed)
4. **Email Preview**: Shows template structure but variables like {magic_link_url} appear as-is

## Future Enhancements

Consider adding:
- [ ] Activity logs (audit trail of admin actions)
- [ ] Bulk user operations (bulk plan updates)
- [ ] User impersonation (login as user for support)
- [ ] System settings panel (rate limits, features)
- [ ] Analytics charts (user growth, analysis trends)
- [ ] CSV export for user data
- [ ] Email test send feature
- [ ] Template version history
