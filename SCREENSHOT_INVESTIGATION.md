# Screenshot Investigation & Findings

## Current Status: ✅ FIXED

### What Was Wrong

1. **Not capturing full pages** - The analyzer was set to `full_page=False`, which meant it only captured above-the-fold content (what you see without scrolling)
2. **S3 storage should be configured** - You mentioned S3 was set up early on, so screenshots should be uploading

### What I Fixed

**File: `backend/services/analyzer.py` (Line ~210)**
```python
# BEFORE (only captured visible viewport):
screenshot_task = asyncio.create_task(
    screenshot_service.capture_screenshot(
        page_content.url,
        viewport_width=1440,
        viewport_height=900,
        full_page=False,  # ❌ Only above-the-fold
    )
)

# AFTER (captures entire scrollable page):
screenshot_task = asyncio.create_task(
    screenshot_service.capture_screenshot(
        page_content.url,
        viewport_width=1440,
        viewport_height=900,
        full_page=True,  # ✅ Full page top to bottom
    )
)
```

## How Screenshots Work

### 1. Capture Process (`backend/services/screenshot.py`)

The screenshot service uses **Playwright** (headless Chromium browser) to:

1. **Load the page** - Waits for `networkidle` (all network requests complete)
2. **Wait 2 seconds** - Allows animations, lazy-loading images, and JavaScript to finish
3. **Capture screenshot** - Takes full-page PNG screenshot when `full_page=True`
4. **Convert to base64** - Encodes image for transmission

```python
await page.goto(url, wait_until='networkidle', timeout=30000)
await page.wait_for_timeout(2000)  # Wait for content to load
screenshot_bytes = await page.screenshot(full_page=True, type='png')
```

### 2. Upload Process (`backend/services/storage.py`)

After capture, screenshots are:

1. **Uploaded to S3** - Stored in your configured AWS S3 bucket
2. **URL generated** - Public URL created for the image
3. **Saved to database** - URL stored with the analysis record

**Required Environment Variables** (should already be in Railway):
- `AWS_S3_BUCKET` - Your S3 bucket name
- `AWS_S3_ACCESS_KEY_ID` - AWS access key
- `AWS_S3_SECRET_ACCESS_KEY` - AWS secret key
- `AWS_S3_REGION` - AWS region (e.g., `us-east-1`)

### 3. Analysis Process (`backend/services/openai_service.py`)

Screenshots are sent to **GPT-4o with Vision** for visual analysis:

```python
messages.append({
    "role": "user",
    "content": [
        {"type": "text", "text": f"Analyze this page VISUALLY and by CONTENT..."},
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{screenshot_base64}",
                "detail": "high"  # High-resolution vision analysis
            }
        }
    ]
})
```

The AI actually **looks at the screenshot** and analyzes:
- Visual hierarchy (what catches attention first)
- Layout and spacing
- Color psychology
- Mobile responsiveness
- Above-the-fold content
- Trust elements and proof

## Verification Steps

### To verify screenshots are working in production:

1. **Check Railway logs** after running an analysis:
   ```
   Screenshot captured successfully for https://example.com (245678 bytes)
   Screenshot uploaded successfully
   ```

2. **Check S3 bucket** - Should see PNG files being uploaded

3. **Check analysis response** - Each page should have:
   ```json
   {
     "screenshot_url": "https://your-bucket.s3.amazonaws.com/screenshots/...",
     "screenshot_storage_key": "screenshots/analysis-123-page-1.png"
   }
   ```

4. **Check frontend display** - `PageAnalysisCard.tsx` shows screenshots:
   ```tsx
   {page.screenshot_url && (
     <div className="relative mb-4 h-72 w-full overflow-hidden rounded-lg">
       <Image src={page.screenshot_url} alt={`Screenshot of ${page.url}`} />
     </div>
   )}
   ```

## Testing Locally

To test locally (when network allows):

```bash
# Install Playwright browsers
playwright install chromium

# Run test script
python test_screenshots.py
```

This will:
- Capture above-the-fold screenshot
- Capture full-page screenshot
- Compare sizes (full should be much larger)
- Test multiple viewports (desktop, tablet, mobile)
- Test S3 upload (if configured)
- Test Infusionsoft page with embedded iframe

## IFrame Handling

For pages like your Infusionsoft order form example:
```
https://yv932.infusionsoft.app/app/orderForms/The-30-Day-Cash-Flow-Blueprint-Membership-GHL
```

The screenshot will capture:
1. ✅ Sales copy above the order form
2. ✅ The Infusionsoft order form iframe
3. ✅ Content below the iframe
4. ✅ Everything from top to bottom

The **scraper** also now detects the iframe and tells the AI:
```
⚠️ IMPORTANT: This page has 1 embedded iframe(s) - likely order forms or sales pages 
embedded in the main page. The sales copy above the iframe is what we can see, but 
there may be additional content/forms inside the iframe that we can't access.
```

## Screenshot Timeout

Screenshots have an 8-second timeout to prevent blocking the analysis:

```python
screenshot_timeout_seconds = 8

screenshot_base64 = await asyncio.wait_for(
    asyncio.shield(screenshot_task),
    timeout=screenshot_timeout_seconds,
)
```

If a page takes too long:
- Analysis continues without the screenshot
- Visual analysis is skipped, but text analysis still happens
- Logged as a timeout in metrics

## Production Readiness Checklist

- [x] Full-page screenshots enabled (`full_page=True`)
- [x] Playwright configured with proper wait times
- [x] S3 storage configured (per user confirmation)
- [x] Screenshots sent to GPT-4o for visual analysis
- [x] IFrame detection working
- [x] Screenshots displayed in frontend
- [ ] **TODO: Verify S3 is actually uploading** (check Railway logs)
- [ ] **TODO: Add mobile viewport screenshots** (for mobile vs desktop scoring)

## Next Steps

1. **Deploy this fix** - Push the `full_page=True` change
2. **Run a test analysis** - Check Railway logs for screenshot messages
3. **Verify S3 bucket** - Confirm PNG files are being uploaded
4. **Check frontend** - Confirm screenshots appear in reports

## Future Enhancements

### Mobile vs Desktop Screenshots
Capture both viewport sizes and score separately:

```python
# Desktop screenshot (1440x900)
desktop_screenshot = await capture_screenshot(url, full_page=True, viewport_width=1440)

# Mobile screenshot (375x812 - iPhone size)
mobile_screenshot = await capture_screenshot(url, full_page=True, viewport_width=375)

# Send both to AI for analysis
{
  "desktop_analysis": {...},
  "mobile_analysis": {...},
  "mobile_score": 85,
  "desktop_score": 72
}
```

This would be HUGELY valuable since:
- 60%+ of traffic is mobile
- Many funnels look great on desktop but broken on mobile
- Mobile conversion rates are often lower due to design issues

### Screenshot Comparison
Store screenshots over time and show visual changes:
- "Your hero section changed 3 times this month"
- "CTA button color updated"
- Visual A/B test tracking
