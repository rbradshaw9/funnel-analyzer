# S3 Permissions Fix - Access Denied Error

## Problem
Screenshot URLs return `<Code>AccessDenied</Code>` when accessed directly. This means:
- ✅ Screenshots ARE being captured by Playwright
- ✅ Screenshots ARE being uploaded to S3
- ✅ URLs ARE being saved to database
- ❌ S3 bucket is NOT allowing public read access

---

## Solution Options

### Option 1: Make Bucket Publicly Readable (Recommended)

#### Step 1: Update Bucket Policy
Go to AWS S3 Console → `funnel-analyzer-pro` bucket → Permissions → Bucket Policy

Add this policy:
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

#### Step 2: Disable "Block Public Access"
Go to Permissions → Block public access (bucket settings) → Edit

**Turn OFF** all 4 checkboxes:
- ❌ Block public access to buckets and objects granted through new access control lists (ACLs)
- ❌ Block public access to buckets and objects granted through any access control lists (ACLs)
- ❌ Block public access to buckets and objects granted through new public bucket or access point policies
- ❌ Block public access to buckets and objects granted through any public bucket or access point policies

Click "Save changes" and confirm.

#### Step 3: Add CORS Configuration (if needed for Next.js)
Go to Permissions → Cross-origin resource sharing (CORS) → Edit

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
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]
```

---

### Option 2: Use Pre-Signed URLs (More Secure)

If you don't want to make the entire bucket public, you can generate temporary signed URLs that expire.

#### Backend Changes Required:

**1. Update `backend/services/storage.py`:**

```python
async def upload_base64_image(
    self,
    *,
    base64_data: str,
    content_type: str = "image/png",
    prefix: str = "screenshots/",
) -> Optional[StoredObject]:
    """Upload a base64 encoded image and return key + signed URL."""
    
    if not base64_data:
        return None

    try:
        binary = base64.b64decode(base64_data)
    except Exception as exc:
        logger.error("Failed to decode screenshot base64 payload: %s", exc)
        return None

    extension = mimetypes.guess_extension(content_type) or ".png"
    key = f"{prefix}{uuid.uuid4().hex}{extension}"

    loop = asyncio.get_running_loop()

    try:
        # Upload WITHOUT public ACL
        await loop.run_in_executor(None, self._put_object_sync, key, binary, content_type)
    except Exception as exc:
        logger.error("Screenshot upload error: %s", exc)
        return None

    # Generate pre-signed URL (valid for 7 days)
    url = self._generate_presigned_url(key, expiry_seconds=604800)
    return StoredObject(key=key, url=url) if url else None

def _generate_presigned_url(self, key: str, expiry_seconds: int = 3600) -> Optional[str]:
    """Generate a pre-signed URL for temporary access."""
    try:
        url = self._client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': self._config.bucket,
                'Key': key
            },
            ExpiresIn=expiry_seconds
        )
        return url
    except Exception as exc:
        logger.error("Failed to generate presigned URL for %s: %s", key, exc)
        return None
```

**Pros**: More secure, no public bucket access needed
**Cons**: URLs expire (need to regenerate), more complex

---

### Option 3: Use CloudFront CDN (Best for Production)

Create a CloudFront distribution in front of your S3 bucket for better performance and security.

#### Benefits:
- ✅ Faster global delivery
- ✅ HTTPS by default
- ✅ Can use custom domain (screenshots.funnelanalyzerpro.com)
- ✅ More control over caching
- ✅ S3 bucket stays private

#### Setup Steps:
1. Create CloudFront distribution pointing to S3 bucket
2. Create Origin Access Identity (OAI)
3. Update S3 bucket policy to only allow CloudFront
4. Set `AWS_S3_BASE_URL` env var to CloudFront domain
5. Update Next.js `remotePatterns` to include CloudFront domain

---

## Quick Fix (Do This Now)

### AWS Console Steps:

1. **Go to S3 Console**: https://console.aws.amazon.com/s3/
2. **Click on `funnel-analyzer-pro` bucket**
3. **Go to Permissions tab**
4. **Scroll to "Block public access" section**
5. **Click "Edit"**
6. **UNCHECK all 4 boxes** (allow public access)
7. **Click "Save changes"**
8. **Type "confirm" when prompted**
9. **Scroll to "Bucket policy" section**
10. **Click "Edit"**
11. **Paste this policy**:
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
12. **Click "Save changes"**

### Test It:
1. Copy a screenshot URL from database or logs
2. Paste into browser
3. Should now show the image (not Access Denied)
4. Run a new analysis
5. Screenshots should appear in the report

---

## Alternative: AWS CLI Commands

If you prefer CLI:

```bash
# Install AWS CLI if not already installed
brew install awscli

# Configure AWS credentials
aws configure
# Enter: Access Key ID, Secret Access Key, Region (us-east-1)

# Disable block public access
aws s3api put-public-access-block \
  --bucket funnel-analyzer-pro \
  --public-access-block-configuration \
  "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

# Apply bucket policy for public read
aws s3api put-bucket-policy \
  --bucket funnel-analyzer-pro \
  --policy '{
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
  }'

# Verify policy was applied
aws s3api get-bucket-policy --bucket funnel-analyzer-pro
```

---

## Verification Checklist

After applying fixes:
- [ ] Visit screenshot URL in browser → Should show image (not Access Denied)
- [ ] Run new analysis → Screenshots should appear
- [ ] Check browser console → No CORS errors
- [ ] Test on different browsers → All should work
- [ ] Check mobile → Screenshots load correctly

---

## Security Considerations

### Public Bucket (Option 1)
**Pros**: Simple, fast, no URL expiration
**Cons**: Anyone with URL can view screenshots

**Mitigation**:
- Use UUID filenames (unpredictable URLs)
- Don't include sensitive information in screenshots
- Add lifecycle policy to delete old screenshots after 90 days

### Pre-Signed URLs (Option 2)
**Pros**: More secure, bucket stays private
**Cons**: URLs expire, need refresh mechanism

### CloudFront (Option 3)
**Pros**: Best performance, most control, HTTPS
**Cons**: Additional AWS service, more setup

---

## Recommended Approach

For now: **Use Option 1 (Public Bucket)**
- Simplest solution
- Works immediately
- Screenshots are already public-facing in reports
- UUID filenames provide obscurity

For later: **Migrate to CloudFront (Option 3)**
- Better performance
- Custom domain
- Enhanced security
- Caching benefits

---

## Next Steps After Fix

1. ✅ Fix S3 permissions (Option 1 above)
2. Test screenshot URLs directly
3. Run new analysis to verify
4. Consider implementing:
   - S3 lifecycle policy (auto-delete old screenshots after 90 days)
   - CloudFront distribution for performance
   - Image optimization/compression before upload
   - Thumbnail generation for faster page loads

---

## Related Environment Variables

Make sure these are set in Railway:
```bash
AWS_S3_BUCKET=funnel-analyzer-pro
AWS_S3_REGION=us-east-1
AWS_S3_ACCESS_KEY_ID=AKIA...
AWS_S3_SECRET_ACCESS_KEY=...

# Optional - if using CloudFront later
AWS_S3_BASE_URL=https://screenshots.funnelanalyzerpro.com
```
