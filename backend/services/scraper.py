"""Web scraping service for extracting content from funnel pages."""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, List, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class PageContent:
    """Structured content extracted from a web page."""
    
    def __init__(
        self,
        url: str,
        title: str,
        headings: List[str],
        paragraphs: List[str],
        ctas: List[str],
        meta_description: Optional[str] = None,
    ):
        self.url = url
        self.title = title
        self.headings = headings
        self.paragraphs = paragraphs
        self.ctas = ctas
        self.meta_description = meta_description
    
    def get_full_text(self) -> str:
        """Combine all text content for analysis."""
        parts = [
            f"Title: {self.title}",
            f"Meta Description: {self.meta_description or 'None'}",
            "\nHeadings:",
            *[f"- {h}" for h in self.headings[:10]],  # Limit to prevent token overflow
            "\nKey Content:",
            *[p[:500] for p in self.paragraphs[:5]],  # Limit paragraph length
            "\nCalls-to-Action:",
            *[f"- {cta}" for cta in self.ctas[:10]],
        ]
        return "\n".join(parts)


async def scrape_url(url: str, timeout: int = 30) -> PageContent:
    """
    Scrape a single URL and extract relevant content.
    
    Args:
        url: The URL to scrape
        timeout: Request timeout in seconds
        
    Returns:
        PageContent object with extracted data
        
    Raises:
        Exception: If scraping fails
    """
    logger.info(f"Scraping URL: {url}")
    
    try:
        # Run synchronous requests in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: requests.get(
                url,
                timeout=timeout,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; FunnelAnalyzer/1.0; +https://funnelanalyzer.pro)"
                },
            ),
        )
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "lxml")
        
        # Extract title
        title = soup.title.string.strip() if soup.title else urlparse(url).path
        
        # Extract meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        meta_description = meta_desc.get("content", "").strip() if meta_desc else None
        
        # Extract headings (h1, h2, h3)
        headings = []
        for tag in ["h1", "h2", "h3"]:
            for heading in soup.find_all(tag):
                text = heading.get_text(strip=True)
                if text:
                    headings.append(text)
        
        # Extract paragraphs
        paragraphs = []
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if text and len(text) > 20:  # Filter out very short paragraphs
                paragraphs.append(text)
        
        # Extract CTAs (buttons, links with action words)
        ctas = []
        cta_keywords = ["buy", "order", "get", "start", "join", "sign", "subscribe", "download", "try", "claim"]
        
        # Find buttons
        for button in soup.find_all(["button", "input"]):
            text = button.get_text(strip=True) or button.get("value", "")
            if text:
                ctas.append(text)
        
        # Find links that look like CTAs
        for link in soup.find_all("a"):
            text = link.get_text(strip=True)
            if text and any(keyword in text.lower() for keyword in cta_keywords):
                ctas.append(text)
        
        logger.info(
            f"Scraped {url}: {len(headings)} headings, {len(paragraphs)} paragraphs, {len(ctas)} CTAs"
        )
        
        return PageContent(
            url=url,
            title=title,
            headings=headings,
            paragraphs=paragraphs,
            ctas=ctas,
            meta_description=meta_description,
        )
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to scrape {url}: {str(e)}")
        raise Exception(f"Failed to fetch page: {str(e)}")
    except Exception as e:
        logger.error(f"Error parsing {url}: {str(e)}")
        raise Exception(f"Failed to parse page content: {str(e)}")


async def scrape_funnel(urls: List[str]) -> List[PageContent]:
    """
    Scrape multiple URLs in parallel.
    
    Args:
        urls: List of URLs to scrape
        
    Returns:
        List of PageContent objects in the same order as input URLs
    """
    logger.info(f"Scraping funnel with {len(urls)} pages")
    
    tasks = [scrape_url(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Convert exceptions to error PageContent objects
    page_contents = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.warning(f"Failed to scrape {urls[i]}: {str(result)}")
            # Create minimal content for failed pages
            page_contents.append(
                PageContent(
                    url=urls[i],
                    title=f"Failed to load: {urls[i]}",
                    headings=[],
                    paragraphs=[f"Error: {str(result)}"],
                    ctas=[],
                )
            )
        else:
            page_contents.append(result)
    
    return page_contents
