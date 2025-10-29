# Screenshot Cleanup System

## Overview

Screenshots are automatically cleaned up from S3 storage to prevent indefinite accumulation and manage costs.

## Automatic Cleanup Triggers

### 1. **User Deletion** ✅
When an admin deletes a user, ALL their screenshots are automatically removed from S3.

```
Admin deletes user → Cleanup service removes all screenshots → User and analyses deleted
```

### 2. **Analysis Deletion** ✅  
When a user or admin deletes an analysis, associated screenshots are removed.

```
DELETE /api/reports/detail/{analysis_id} → Screenshots deleted from S3
```

## Manual Cleanup (Admin Endpoints)

### Expired Free Trials
**Endpoint**: `POST /api/admin/screenshots/cleanup/expired-trials`

Deletes screenshots from free accounts older than 14 days that never converted to paid.

**Headers**: `Authorization: Bearer {admin_token}`

**Response**:
```json
{
  "screenshots_deleted": 42,
  "message": "Cleaned up 42 screenshots from expired free trials"
}
```

---

### Inactive User Cleanup
**Endpoint**: `POST /api/admin/screenshots/cleanup/inactive-users`

For users who haven't logged in for 90+ days:
- Deletes screenshots older than 30 days
- Keeps recent screenshots (last 30 days)

**Headers**: `Authorization: Bearer {admin_token}`

**Response**:
```json
{
  "screenshots_deleted": 156,
  "message": "Cleaned up 156 old screenshots from inactive users"
}
```

---

### Storage Statistics
**Endpoint**: `GET /api/admin/screenshots/storage/stats`

View current screenshot storage usage across all users.

**Headers**: `Authorization: Bearer {admin_token}`

**Response**:
```json
{
  "total_screenshots": 1248,
  "by_plan": {
    "free": 420,
    "basic": 528,
    "pro": 300
  },
  "old_screenshots_90_days": 89,
  "estimated_storage_mb": 624.0
}
```

---

## Cleanup Policies

| Scenario | Retention Policy |
|----------|------------------|
| **Active paid users** | Keep all screenshots indefinitely |
| **Free trial (converted)** | Keep all screenshots |
| **Free trial (expired)** | Delete after 14 days |
| **Inactive users (90+ days)** | Keep last 30 days, delete older |
| **User deleted** | Delete ALL immediately |
| **Analysis deleted** | Delete ALL immediately |

## Storage Estimates

- **Average screenshot size**: ~500KB
- **Per analysis** (5 pages): ~2.5MB
- **1000 analyses**: ~2.5GB

## Scheduled Cleanup (Future Enhancement)

Consider adding a cron job to run cleanup automatically:

```python
# Example: Daily cleanup at 2 AM
# Endpoint: POST /api/admin/screenshots/cleanup/expired-trials
# Run via cron or Railway scheduled task
```

## Frontend Integration

The admin dashboard can display storage stats and provide cleanup buttons:

```tsx
// Admin Dashboard - Storage Management
<StorageStatsCard>
  <StatDisplay label="Total Screenshots" value={1248} />
  <StatDisplay label="Storage Used" value="624 MB" />
  <Button onClick={cleanupExpiredTrials}>
    Clean Expired Trials
  </Button>
  <Button onClick={cleanupInactiveUsers}>
    Clean Inactive Users
  </Button>
</StorageStatsCard>
```

## Implementation Details

### Files
- `backend/services/screenshot_cleanup.py` - Core cleanup logic
- `backend/routes/cleanup.py` - Admin API endpoints
- `backend/routes/admin.py` - User deletion with cleanup
- `backend/services/reports.py` - Analysis deletion with cleanup

### Database
Screenshots tracked via:
- `page_analyses.screenshot_url` - Public S3 URL
- `page_analyses.screenshot_storage_key` - S3 object key for deletion

### S3 Operations
- **Upload**: `storage_service.upload_base64_image()`
- **Delete**: `storage_service.delete_object(key)`

## Testing

```python
# Test user deletion cleanup
DELETE /api/admin/users/123
# Should log: "Deleted N screenshots for user email@example.com"

# Test analysis deletion
DELETE /api/reports/detail/456
# Should return: {"assets_deleted": 5, "assets_failed": 0}

# Test manual cleanup
POST /api/admin/screenshots/cleanup/expired-trials
# Should return: {"screenshots_deleted": X, "message": "..."}
```

## Cost Savings

**Before**: Screenshots accumulate indefinitely  
**After**: 
- Free trials cleaned after 14 days
- Inactive users cleaned after 90 days
- Deleted users/analyses cleaned immediately

**Estimated savings**: 40-60% reduction in S3 storage costs for typical usage patterns.
