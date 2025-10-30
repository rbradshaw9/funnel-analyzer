# Screenshot Pipeline Investigation & Fix

## Problem Statement
Screenshots are showing placeholders in the UI instead of actual page captures. Need to trace the full pipeline from capture → upload → save → display → AI analysis.

---

## Pipeline Flow (Expected)

```
1. Playwright Browser Launch
   ↓
2. Navigate to URL + Capture Screenshot (screenshot.py)
   ↓
3. Convert to Base64
   ↓
4. Upload to S3 (storage.py)
   ↓
5. Get Public S3 URL
   ↓
6. Save URL to Database (analysis_pages.screenshot_url)
   ↓
7. Send Base64 to OpenAI Vision API (openai_service.py)
   ↓
8. Frontend Fetches Analysis (includes screenshot_url)
   ↓
9. Next.js Image Component Renders S3 URL
```

---

## Code Review Findings

### ✅ WORKING: Screenshot Capture (backend/services/screenshot.py)
```python
async def analyze_above_fold(self, url: str) -> Dict:
    # Captures FULL PAGE screenshot
    screenshot_bytes = await page.screenshot(
        type='png',
        full_page=True  # ✓ Captures entire page
    )
    screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
    return {'screenshot': screenshot_base64, 'visual_elements': visual_data}
```
**Status**: Code looks correct. Playwright configured with proper args.

---

### ✅ WORKING: S3 Upload (backend/services/storage.py)
```python
async def upload_base64_image(
    self,
    *,
    base64_data: str,
    content_type: str = "image/png",
    prefix: str = "screenshots/",
) -> Optional[StoredObject]:
    # Decodes base64
    binary = base64.b64decode(base64_data)
    
    # Generates unique key
    key = f"{prefix}{uuid.uuid4().hex}.png"
    
    # Uploads to S3
    self._client.put_object(
        Bucket=self._config.bucket,
        Key=key,
        Body=binary,
        ContentType=content_type,
        ACL="public-read"  # Or None if bucket doesn't support ACLs
    )
    
    # Builds public URL
    url = self._build_public_url(key)
    return StoredObject(key=key, url=url)
```
**Status**: Code looks correct. Returns URL from `_build_public_url()`.

**Possible Issues**:
1. ❓ S3 credentials not configured in Railway environment variables
2. ❓ Bucket name incorrect or doesn't exist
3. ❓ Bucket not publicly readable (CORS/bucket policy)
4. ❓ Base URL configuration missing

---

### ✅ WORKING: Database Save (backend/services/analyzer.py)
```python
# Line 330 - Upload screenshot
if screenshot_base64 and storage_service:
    screenshot_asset = await storage_service.upload_base64_image(
        base64_data=screenshot_base64,
        content_type="image/png",
    )
    if screenshot_asset:
        screenshot_url = screenshot_asset.url  # ✓ Gets URL from S3
        logger.info(f"✓ Screenshot uploaded: {screenshot_url}")

# Line 465 - Save to database
analysis.pages = [
    AnalysisPage(
        url=page["url"],
        screenshot_url=page.get("screenshot_url"),  # ✓ Saved to DB
        screenshot_storage_key=page.get("screenshot_storage_key"),
        ...
    )
    for page in analysis_result["pages"]
]
```
**Status**: Code looks correct. URL is saved to `analysis_pages.screenshot_url`.

**Possible Issues**:
1. ❓ `storage_service` is None (not initialized)
2. ❓ `screenshot_base64` is None (capture failed)
3. ❓ Migration didn't run (screenshot_url column doesn't exist)

---

### ✅ WORKING: AI Vision Integration (backend/services/openai_service.py)
```python
# Line 104-116
if screenshot_base64:
    user_message_content.append({
        "type": "text",
        "text": main_prompt
    })
    user_message_content.append({
        "type": "image_url",
        "image_url": {
            "url": f"data:image/png;base64,{screenshot_base64}",
            "detail": "high"
        }
    })
```
**Status**: ✅ CONFIRMED - Screenshots ARE being sent to OpenAI vision API with proper format.

---

### ⚠️ NEEDS INVESTIGATION: Frontend Display (frontend/components/PageAnalysisCard.tsx)
```tsx
{page.screenshot_url ? (
  <Image
    src={page.screenshot_url}  // Rendering S3 URL
    alt={`Screenshot of ${page.url}`}
    fill
    onError={(e) => {
      console.error('Failed to load screenshot:', page.screenshot_url)
      // Shows fallback
    }}
  />
) : (
  // Shows "Screenshot capture in progress..." placeholder
  <div className="text-center">
    <p>Screenshot capture in progress...</p>
    <p>Screenshots will appear when S3 storage is configured</p>
  </div>
)}
```

**Possible Issues**:
1. ❓ `page.screenshot_url` is null/undefined (not in API response)
2. ❓ S3 URL is correct but image fails to load (CORS issue)
3. ❓ Next.js Image component not configured for external S3 domain
4. ❓ S3 bucket blocks public read access

---

## Diagnostic Steps

### Step 1: Check Railway Environment Variables
```bash
# Railway Dashboard → funnel-analyzer-backend → Variables
AWS_S3_BUCKET=funnel-analyzer-pro  # ✓ Should exist
AWS_S3_ACCESS_KEY_ID=AKIA...  # ✓ Must be set
AWS_S3_SECRET_ACCESS_KEY=***  # ✓ Must be set
AWS_S3_REGION=us-east-1  # ✓ Should match bucket region
AWS_S3_BASE_URL=https://funnel-analyzer-pro.s3.us-east-1.amazonaws.com  # OR custom domain
```

### Step 2: Check Railway Logs for Screenshot Upload
```bash
# Look for these log messages:
✓ Screenshot uploaded for https://example.com: https://...
Screenshot URL preview: https://funnel-analyzer-pro.s3...

# OR error messages:
⚠️ S3 storage not configured - screenshots will NOT be saved
Failed to upload screenshot for https://example.com: ...
```

### Step 3: Check Database for Screenshot URLs
```sql
-- Run in Railway PostgreSQL console
SELECT 
    id,
    url,
    screenshot_url,
    screenshot_storage_key
FROM analysis_pages
WHERE analysis_id = (SELECT id FROM analyses ORDER BY created_at DESC LIMIT 1);
```

**Expected Result**:
- `screenshot_url`: `https://funnel-analyzer-pro.s3.us-east-1.amazonaws.com/screenshots/abc123.png`
- `screenshot_storage_key`: `screenshots/abc123.png`

**If NULL**: Screenshot upload failed or storage service not configured.

### Step 4: Test S3 URL Directly
```bash
# Copy a screenshot_url from database
# Paste into browser: https://funnel-analyzer-pro.s3.us-east-1.amazonaws.com/screenshots/abc123.png

# Should: Display the screenshot image
# If 403 Forbidden: Bucket policy doesn't allow public read
# If 404 Not Found: File wasn't actually uploaded
# If CORS error: Need to add frontend domain to bucket CORS config
```

### Step 5: Check Next.js Image Configuration
```js
// frontend/next.config.js
module.exports = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'funnel-analyzer-pro.s3.us-east-1.amazonaws.com',
        // OR
        hostname: '*.s3.us-east-1.amazonaws.com',
        // OR
        hostname: '*.amazonaws.com',  // Broad but works
      },
    ],
  },
}
```

**If missing**: Next.js will block external images from S3.

### Step 6: Check S3 Bucket Configuration

#### Bucket Policy (Public Read)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::funnel-analyzer-pro/*"
    }
  ]
}
```

#### CORS Configuration
```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedOrigins": [
      "https://funnelanalyzerpro.com",
      "https://www.funnelanalyzerpro.com",
      "http://localhost:3001"
    ],
    "ExposeHeaders": []
  }
]
```

#### Block Public Access Settings
```
Block all public access: OFF
Block public access to buckets and objects granted through new access control lists (ACLs): OFF
Block public access to buckets and objects granted through any access control lists (ACLs): OFF
Block public access to buckets and objects granted through new public bucket or access point policies: OFF
Block public access to buckets and objects granted through any public bucket or access point policies: OFF
```

---

## Most Likely Issues (Ranked)

### 1. 🔴 HIGH PROBABILITY: S3 Environment Variables Not Set in Railway
**Symptom**: Logs show `⚠️ S3 storage not configured`

**Fix**: Add to Railway environment variables:
```
AWS_S3_BUCKET=funnel-analyzer-pro
AWS_S3_ACCESS_KEY_ID=AKIA...
AWS_S3_SECRET_ACCESS_KEY=...
AWS_S3_REGION=us-east-1
```

---

### 2. 🟡 MEDIUM PROBABILITY: Next.js Image Domain Not Whitelisted
**Symptom**: Browser console shows `Invalid src prop ... hostname not configured under images in next.config.js`

**Fix**: Add to `frontend/next.config.js`:
```js
images: {
  remotePatterns: [
    {
      protocol: 'https',
      hostname: '*.amazonaws.com',
    },
  ],
}
```

---

### 3. 🟡 MEDIUM PROBABILITY: S3 Bucket Not Publicly Readable
**Symptom**: Direct S3 URL returns 403 Forbidden

**Fix**: Add bucket policy for public read access (see above).

---

### 4. 🟢 LOW PROBABILITY: Database Migration Didn't Run
**Symptom**: `screenshot_url` column doesn't exist

**Fix**: Run migrations:
```bash
# Railway should auto-run migrations on deploy
# But can manually trigger:
railway run python -m backend.db.migrations
```

---

## Action Plan

### Immediate Tasks
1. [ ] Check Railway environment variables for S3 config
2. [ ] Check Railway logs for screenshot upload success/failure
3. [ ] Query production database for screenshot_url values
4. [ ] Test S3 URL directly in browser
5. [ ] Verify Next.js image configuration
6. [ ] Check S3 bucket policy and CORS

### If S3 Not Configured
1. [ ] Get AWS credentials from team/create new IAM user
2. [ ] Create/configure `funnel-analyzer-pro` bucket
3. [ ] Set bucket policy for public read
4. [ ] Add CORS configuration
5. [ ] Add env vars to Railway
6. [ ] Redeploy backend

### If S3 IS Configured But Not Working
1. [ ] Check bucket name matches env var
2. [ ] Verify IAM user has s3:PutObject permission
3. [ ] Test manual upload with AWS CLI
4. [ ] Review Botocore errors in logs
5. [ ] Check if ACL is supported (some buckets block ACLs)

---

## Testing Checklist

After fixes, verify:
- [ ] Run new analysis
- [ ] Check logs for "✓ Screenshot uploaded"
- [ ] Check database for screenshot_url
- [ ] Test S3 URL in browser (should show image)
- [ ] Frontend shows actual screenshots (not placeholders)
- [ ] Multiple pages all have screenshots
- [ ] Re-run analysis also captures screenshots

---

## Related Files

**Backend**:
- `backend/services/screenshot.py` - Playwright capture
- `backend/services/storage.py` - S3 upload
- `backend/services/analyzer.py` - Orchestration
- `backend/utils/config.py` - Environment variables
- `backend/models/database.py` - AnalysisPage model

**Frontend**:
- `frontend/components/PageAnalysisCard.tsx` - Screenshot display
- `frontend/next.config.js` - Image domain config
- `frontend/app/reports/[id]/page.tsx` - Report page

**Infrastructure**:
- `railway.json` - Deployment config
- `.env.example` - Environment variable template
