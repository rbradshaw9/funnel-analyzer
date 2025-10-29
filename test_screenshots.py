#!/usr/bin/env python3
"""Test script to verify screenshot functionality is working correctly."""

import asyncio
import base64
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.services.screenshot import get_screenshot_service, cleanup_screenshot_service
from backend.services.storage import get_storage_service


async def test_screenshot_capture():
    """Test that screenshots are being captured correctly."""
    print("=" * 60)
    print("Screenshot Service Test")
    print("=" * 60)
    
    test_url = "https://funnelanalyzerpro.com"
    
    try:
        # Get screenshot service
        print("\n1. Initializing screenshot service...")
        screenshot_service = await get_screenshot_service()
        print("✓ Screenshot service initialized")
        
        # Test above-the-fold screenshot
        print(f"\n2. Capturing above-the-fold screenshot of {test_url}...")
        screenshot_base64 = await screenshot_service.capture_screenshot(
            url=test_url,
            viewport_width=1440,
            viewport_height=900,
            full_page=False,
        )
        
        if screenshot_base64:
            size_kb = len(screenshot_base64) / 1024
            print(f"✓ Above-the-fold screenshot captured: {size_kb:.1f} KB (base64)")
            
            # Save to file for inspection
            screenshot_bytes = base64.b64decode(screenshot_base64)
            with open("test_screenshot_above_fold.png", "wb") as f:
                f.write(screenshot_bytes)
            print(f"✓ Saved to: test_screenshot_above_fold.png ({len(screenshot_bytes)/1024:.1f} KB)")
        else:
            print("✗ Failed to capture above-the-fold screenshot")
            return False
        
        # Test full-page screenshot
        print(f"\n3. Capturing FULL PAGE screenshot of {test_url}...")
        screenshot_full = await screenshot_service.capture_screenshot(
            url=test_url,
            viewport_width=1440,
            viewport_height=900,
            full_page=True,
        )
        
        if screenshot_full:
            size_kb = len(screenshot_full) / 1024
            print(f"✓ Full-page screenshot captured: {size_kb:.1f} KB (base64)")
            
            # Save to file for inspection
            screenshot_bytes_full = base64.b64decode(screenshot_full)
            with open("test_screenshot_full_page.png", "wb") as f:
                f.write(screenshot_bytes_full)
            print(f"✓ Saved to: test_screenshot_full_page.png ({len(screenshot_bytes_full)/1024:.1f} KB)")
            
            # Compare sizes
            ratio = len(screenshot_bytes_full) / len(screenshot_bytes)
            print(f"\nℹ️  Full page is {ratio:.1f}x larger than above-the-fold")
            if ratio < 1.2:
                print("⚠️  Warning: Full page screenshot is not much larger - page might be short or full_page isn't working")
        else:
            print("✗ Failed to capture full-page screenshot")
            return False
        
        # Test multiple viewports
        print(f"\n4. Capturing multiple viewport sizes...")
        screenshots = await screenshot_service.capture_multiple_viewports(test_url)
        
        for device, screenshot in screenshots.items():
            if screenshot:
                size_kb = len(screenshot) / 1024
                print(f"✓ {device.capitalize()}: {size_kb:.1f} KB")
                
                # Save each viewport
                screenshot_bytes_device = base64.b64decode(screenshot)
                with open(f"test_screenshot_{device}.png", "wb") as f:
                    f.write(screenshot_bytes_device)
            else:
                print(f"✗ {device.capitalize()}: Failed")
        
        # Test storage upload if configured
        print(f"\n5. Testing S3 storage upload...")
        storage_service = get_storage_service()
        
        if storage_service:
            print("✓ Storage service is configured")
            
            try:
                asset = await storage_service.upload_base64_image(
                    base64_data=screenshot_full,
                    content_type="image/png"
                )
                
                if asset and asset.url:
                    print(f"✓ Screenshot uploaded successfully")
                    print(f"  URL: {asset.url}")
                    print(f"  Key: {asset.key}")
                else:
                    print("✗ Upload returned no URL")
                    return False
                    
            except Exception as e:
                print(f"✗ Upload failed: {str(e)}")
                return False
        else:
            print("⚠️  Storage service not configured (S3 credentials missing)")
            print("   Screenshots will not be saved or displayed in reports")
            print("   Set these Railway environment variables:")
            print("   - AWS_S3_BUCKET")
            print("   - AWS_S3_ACCESS_KEY_ID")
            print("   - AWS_S3_SECRET_ACCESS_KEY")
            print("   - AWS_S3_REGION")
        
        print("\n" + "=" * 60)
        print("✓ Screenshot service is working correctly!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        print("\n6. Cleaning up...")
        await cleanup_screenshot_service()
        print("✓ Cleanup complete")


async def test_infusionsoft_page():
    """Test screenshot of an Infusionsoft page with embedded content."""
    print("\n" + "=" * 60)
    print("Testing Infusionsoft Order Form Page")
    print("=" * 60)
    
    test_url = "https://yv932.infusionsoft.app/app/orderForms/The-30-Day-Cash-Flow-Blueprint-Membership-GHL"
    
    try:
        screenshot_service = await get_screenshot_service()
        
        print(f"\nCapturing full page of Infusionsoft order form...")
        screenshot_base64 = await screenshot_service.capture_screenshot(
            url=test_url,
            viewport_width=1440,
            viewport_height=900,
            full_page=True,
        )
        
        if screenshot_base64:
            screenshot_bytes = base64.b64decode(screenshot_base64)
            size_kb = len(screenshot_bytes) / 1024
            
            with open("test_infusionsoft_page.png", "wb") as f:
                f.write(screenshot_bytes)
            
            print(f"✓ Infusionsoft page captured: {size_kb:.1f} KB")
            print(f"✓ Saved to: test_infusionsoft_page.png")
            print("\nThis should show:")
            print("  • Sales copy above the order form")
            print("  • The embedded Infusionsoft order form")
            print("  • Full page scrolled content")
            
            return True
        else:
            print("✗ Failed to capture Infusionsoft page")
            return False
            
    except Exception as e:
        print(f"✗ Error capturing Infusionsoft page: {str(e)}")
        return False
    finally:
        await cleanup_screenshot_service()


async def main():
    """Run all tests."""
    print("\n🔍 Testing Screenshot Functionality\n")
    
    # Check if Playwright is installed
    try:
        import playwright
        print("✓ Playwright is installed")
    except ImportError:
        print("✗ Playwright is not installed!")
        print("\nInstall with: pip install playwright")
        print("Then run: playwright install chromium")
        return False
    
    # Test basic screenshot functionality
    success = await test_screenshot_capture()
    
    if success:
        # Test Infusionsoft page
        infusionsoft_success = await test_infusionsoft_page()
        
        if infusionsoft_success:
            print("\n✅ All tests passed!")
            print("\nGenerated test images:")
            print("  • test_screenshot_above_fold.png")
            print("  • test_screenshot_full_page.png")
            print("  • test_screenshot_desktop.png")
            print("  • test_screenshot_tablet.png")
            print("  • test_screenshot_mobile.png")
            print("  • test_infusionsoft_page.png")
            print("\nOpen these images to verify they look correct.")
        else:
            print("\n⚠️  Basic tests passed but Infusionsoft test failed")
    else:
        print("\n❌ Screenshot tests failed")
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
