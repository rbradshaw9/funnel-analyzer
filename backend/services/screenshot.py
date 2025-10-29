"""Screenshot service for capturing page visuals with Playwright."""

from __future__ import annotations

import asyncio
import base64
import logging
from pathlib import Path
from typing import Dict, Optional

from playwright.async_api import async_playwright, Browser, Page

logger = logging.getLogger(__name__)


class ScreenshotService:
    """Service for capturing screenshots of web pages."""
    
    def __init__(self):
        self._browser: Optional[Browser] = None
    
    async def __aenter__(self):
        """Context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()
    
    async def start(self):
        """Start the browser."""
        if self._browser is None:
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                ]
            )
            logger.info("Playwright browser started")
    
    async def close(self):
        """Close the browser."""
        if self._browser:
            await self._browser.close()
            self._browser = None
            logger.info("Playwright browser closed")
    
    async def capture_screenshot(
        self,
        url: str,
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        full_page: bool = False,
        wait_for_network_idle: bool = True,
    ) -> str:
        """
        Capture a screenshot of a URL and return as base64 encoded string.
        
        Args:
            url: The URL to screenshot
            viewport_width: Browser viewport width
            viewport_height: Browser viewport height
            full_page: Whether to capture the full scrollable page
            wait_for_network_idle: Wait for network to be idle before screenshot
            
        Returns:
            Base64 encoded PNG screenshot
        """
        if not self._browser:
            await self.start()
        
        logger.info(f"Capturing screenshot of {url}")
        
        try:
            page = await self._browser.new_page(
                viewport={'width': viewport_width, 'height': viewport_height},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            try:
                # Navigate to the page
                await page.goto(
                    url,
                    wait_until='networkidle' if wait_for_network_idle else 'domcontentloaded',
                    timeout=30000  # 30 seconds
                )
                
                # Wait a bit for any animations/lazy loading
                await page.wait_for_timeout(2000)
                
                # Take screenshot
                screenshot_bytes = await page.screenshot(
                    full_page=full_page,
                    type='png',
                )
                
                # Convert to base64
                screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
                
                logger.info(f"Screenshot captured successfully for {url} ({len(screenshot_bytes)} bytes)")
                return screenshot_base64
                
            finally:
                await page.close()
                
        except Exception as e:
            logger.error(f"Failed to capture screenshot of {url}: {str(e)}")
            raise Exception(f"Screenshot capture failed: {str(e)}")
    
    async def capture_multiple_viewports(self, url: str) -> Dict[str, str]:
        """
        Capture screenshots at different viewport sizes (desktop, tablet, mobile).
        
        Args:
            url: The URL to screenshot
            
        Returns:
            Dict with base64 screenshots for each viewport
        """
        viewports = {
            'desktop': {'width': 1920, 'height': 1080},
            'tablet': {'width': 768, 'height': 1024},
            'mobile': {'width': 375, 'height': 812},
        }
        
        screenshots = {}
        
        for device, viewport in viewports.items():
            try:
                screenshot = await self.capture_screenshot(
                    url,
                    viewport_width=viewport['width'],
                    viewport_height=viewport['height'],
                    full_page=False,  # Just above-the-fold for quick analysis
                )
                screenshots[device] = screenshot
                logger.info(f"Captured {device} screenshot for {url}")
            except Exception as e:
                logger.warning(f"Failed to capture {device} screenshot: {str(e)}")
                screenshots[device] = None
        
        return screenshots
    
    async def analyze_above_fold(self, url: str) -> Dict:
        """
        Capture FULL PAGE screenshot and analyze ALL content including CTAs.
        
        Args:
            url: The URL to analyze
            
        Returns:
            Dict with full-page screenshot and extracted visual elements
        """
        if not self._browser:
            await self.start()
        
        logger.info(f"Analyzing full page for {url}")
        
        try:
            page = await self._browser.new_page(
                viewport={'width': 1440, 'height': 900}
            )
            
            try:
                await page.goto(url, wait_until='networkidle', timeout=30000)
                await page.wait_for_timeout(2000)
                
                # Capture FULL PAGE screenshot (entire scrollable content)
                screenshot_bytes = await page.screenshot(
                    type='png',
                    full_page=True  # Capture entire page, not just viewport
                )
                screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
                
                # Extract visual elements from ENTIRE page (not just above-the-fold)
                visual_data = await page.evaluate("""
                    () => {
                        // Get ALL images on the page
                        const images = Array.from(document.querySelectorAll('img'))
                            .map(img => ({
                                src: img.src,
                                alt: img.alt,
                                width: img.width,
                                height: img.height
                            }));
                        
                        // Get ALL CTA buttons on the entire page
                        const buttons = Array.from(document.querySelectorAll('button, a[class*="button"], a[class*="btn"], input[type="submit"], a[role="button"]'))
                            .map(btn => ({
                                text: btn.textContent.trim(),
                                tag: btn.tagName,
                                classes: btn.className,
                                href: btn.href || null
                            }));
                        
                        // Get computed styles of body
                        const bodyStyles = window.getComputedStyle(document.body);
                        
                        return {
                            images: images,
                            buttons: buttons,
                            colors: {
                                background: bodyStyles.backgroundColor,
                                text: bodyStyles.color,
                                primaryFont: bodyStyles.fontFamily
                            },
                            viewportHeight: window.innerHeight,
                            scrollHeight: document.body.scrollHeight,
                            totalButtons: buttons.length,
                            totalImages: images.length
                        };
                    }
                """)
                
                logger.info(
                    f"✓ Full page analysis: {len(visual_data.get('buttons', []))} CTAs, "
                    f"{len(visual_data.get('images', []))} images, "
                    f"{visual_data.get('scrollHeight', 0)}px total height"
                )
                
                return {
                    'screenshot': screenshot_base64,
                    'visual_elements': visual_data
                }
                
            finally:
                await page.close()
                
        except Exception as e:
            logger.error(f"Failed to analyze full page for {url}: {str(e)}")
            raise


# Singleton instance
_screenshot_service: Optional[ScreenshotService] = None


async def get_screenshot_service() -> ScreenshotService:
    """Get or create the screenshot service singleton."""
    global _screenshot_service
    if _screenshot_service is None:
        _screenshot_service = ScreenshotService()
        await _screenshot_service.start()
    return _screenshot_service


async def cleanup_screenshot_service():
    """Clean up the screenshot service."""
    global _screenshot_service
    if _screenshot_service is not None:
        await _screenshot_service.close()
        _screenshot_service = None
