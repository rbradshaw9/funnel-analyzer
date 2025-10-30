# S3 CORS Configuration for Screenshots

## Problem
Browser fetch requests to S3 screenshot URLs from `https://funnelanalyzerpro.com` are blocked by CORS policy:
```
Access to fetch at 'https://funnel-analyzer-pro.s3.amazonaws.com/screenshots/...' 
from origin 'https://funnelanalyzerpro.com' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## Solution
Add CORS configuration to the S3 bucket to allow browser requests from the frontend.

## Steps to Configure

1. Go to [AWS S3 Console](https://s3.console.aws.amazon.com/s3/buckets)
2. Click on bucket `funnel-analyzer-pro`
3. Go to **Permissions** tab
4. Scroll to **Cross-origin resource sharing (CORS)** section
5. Click **Edit**
6. Paste this JSON configuration:

```json
[
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "GET",
            "HEAD"
        ],
        "AllowedOrigins": [
            "https://funnelanalyzerpro.com",
            "http://localhost:3000",
            "http://localhost:3001"
        ],
        "ExposeHeaders": [
            "ETag",
            "Content-Length",
            "Content-Type"
        ],
        "MaxAgeSeconds": 3600
    }
]
```

7. Click **Save changes**

## Explanation

- **AllowedOrigins**: Allows requests from production domain and local development
- **AllowedMethods**: Only GET/HEAD needed for reading screenshots
- **AllowedHeaders**: `*` allows all headers (required for Next.js Image component)
- **ExposeHeaders**: Makes response headers available to browser JavaScript
- **MaxAgeSeconds**: Browser caches CORS preflight for 1 hour

## Testing

After applying CORS config, test by:

1. Open browser DevTools Console
2. Navigate to a report page
3. Run this test fetch:
```javascript
fetch('https://funnel-analyzer-pro.s3.amazonaws.com/screenshots/[UUID].png')
  .then(r => console.log('✅ CORS working:', r.status))
  .catch(e => console.error('❌ CORS failed:', e))
```

Should see `✅ CORS working: 200` instead of CORS error.

## Related Issues

- Screenshot URLs now correctly use single `/screenshots/` path (fixed in storage.py)
- Bucket already has public read policy allowing anonymous access
- CORS is separate from bucket policy - controls browser same-origin restrictions
